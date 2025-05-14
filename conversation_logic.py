
from schemas.ConversationState import ConversationState
from schemas.ValidationResponse import ValidationResponse
from schemas.ElderlyUser import ElderlyUser
import yaml
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langchain.schema.messages import HumanMessage, SystemMessage
from langchain.schema.messages import HumanMessage
from VoiceToText import VoiceToText


class conversation_logic:
    def __init__(self):
        question_config = yaml.safe_load(open('./configs/essential_question_prompts.yaml', 'r', encoding='utf-8'))
        validation_config = yaml.safe_load(open('./configs/validation_prompts.yaml', 'r', encoding='utf-8'))
        output_config = yaml.safe_load(open('./configs/output_format_prompt.yaml', 'r', encoding='utf-8'))
        load_dotenv()

        self.question_list = [question_config['essential_question1'], 
                        question_config['essential_question2'],
                        question_config['essential_question3'],
                        question_config['essential_question4'],
                        question_config['essential_question5'],
                        question_config['essential_question6'],
                        question_config['essential_question7'],
                        question_config['essential_question8'],
                        question_config['essential_question9'],]

        self.validation_list = [validation_config['validation_question1'],
                        validation_config['validation_question1'],
                        validation_config['validation_question1'],
                        validation_config['validation_question1'],
                        validation_config['validation_question1'],
                        validation_config['validation_question1'],
                        validation_config['validation_question1'],
                        validation_config['validation_question1'],
                        validation_config['validation_question1']]
        
        self.output_prompt = output_config['output_format']
        self.gpt = ChatOpenAI(model="gpt-4o-mini",)
        self.valid_gpt = self.gpt.with_structured_output(ValidationResponse)
        self.valid_gpt_output = self.gpt.with_structured_output(ElderlyUser)
        self.vtt = VoiceToText()

#  ---------------------------NODES-----------------------------------------------------

    def initialize(self, state: ConversationState) -> ConversationState:
        self.vtt.speak("안녕하세요. 어르신의 구직을 도와드리기 위해 몇 가지 질문을 드리겠습니다.")
        self.vtt.speak("질문에 대한 답변은 가능한 구체적으로 말씀해주실 수록 최적의 구직 정보를 제공받으실 수 있습니다.")
        self.vtt.speak("그럼 시작하겠습니다.")

        return state

    def conversation(self, state: ConversationState) -> ConversationState:
        phase = state['phase']
        AIquestion = self.question_list[phase]
 
        # TTS로 질문 음성 출력
        self.vtt.speak(AIquestion) 

        # STT로 사용자의 답변 음성 입력
        human_answer = self.vtt.record() 

        # 녹음 실패 또는 STT 실패 시
        if human_answer is None or "[녹음 실패]" in human_answer or "[녹음된 음성이 없습니다]" in human_answer:
            self.vtt.speak("죄송합니다. 음성이 잘 들리지 않았어요. 다시 한 번 천천히 말씀해주시겠어요?")
            return self.retry(state)
        
        # 정상 응답 처리
        print(f"[USER] {human_answer}")
        past_history = state['history']
        new_history = past_history + [f"AI : {AIquestion}\n",]
        new_history = new_history + [f"User : {human_answer}\n"]

        return {'history' : new_history, 'last_response': human_answer }

    def is_valid(self, state: ConversationState) -> str:
        phase = state['phase']
        AIquestion = self.question_list[phase]
        validation_prompt = self.validation_list[phase]
        human_answer = state['last_response']

        validation_input = [SystemMessage(validation_prompt), HumanMessage(f'질문: {AIquestion} \n답변: {human_answer}')]
        justification = self.valid_gpt.invoke(validation_input)
        
        if justification.is_valid:
            if state['phase'] == len(self.question_list) - 1:
                self.vtt.speak("모든 질문에 대한 답변이 끝나셨습니다. \
                                 어르신의 답변을 바탕으로 최적의 구직 정보를 빠른 시일 내에 메세지로 전달해드리겠습니다. \
                                 감사합니다.")
                return "End"
            else:
                state['phase'] += 1
                return  "Next"
        else:
            common_prefix = '어르신, 말씀주신 내용이 충분하지 않은 것 같아요.'
            ai_prefix = justification.message

            self.vtt.speak(f"{common_prefix} {ai_prefix}")
            return "Retry"
        
    def before_next(self, state: ConversationState) -> ConversationState:
        self.vtt.speak("감사합니다. 다음 질문으로 넘어가겠습니다.")
        
        return {'phase': state['phase'] + 1,}

    def before_end(self, state: ConversationState) -> ConversationState:
        self.vtt.speak("어르신, 대화가 종료되었습니다.")
        
        return {'history': state['history'] + [f"[대화 종료]"],}


    def retry(self, state: ConversationState) -> ConversationState:
        new_history = state['history'][:-2]
        return {'history': new_history}
    
# ---------------------------WORKFLOW-----------------------------------------------------


    def compose_workflow(self):
        workflow = StateGraph(ConversationState)

        workflow.add_node(self.initialize, 'initialize')
        workflow.add_node(self.conversation, 'conversation')
        workflow.add_node(self.is_valid, 'is_valid')
        workflow.add_node(self.retry, 'retry')
        workflow.add_node(self.before_next, 'before_next')
        workflow.add_node(self.before_end, 'before_end')

        workflow.add_edge(START, 'initialize')
        workflow.add_edge('initialize', 'conversation')
        workflow.add_edge('retry', 'conversation')
        workflow.add_conditional_edges('conversation',
                                    self.is_valid,
                                    {
                                        "Next": 'before_next',
                                        "Retry": 'retry',
                                            "End": 'before_end'
                                    })
        workflow.add_edge('before_end', END)
        workflow.add_edge('before_next', 'conversation')
        graph = workflow.compile()
        graph.recursion_limit = 50
        self.graph = graph

    def _run(self):
        self.compose_workflow()
        dummy_input = {'phase': 0,
              'history': [],
              'last_response': "",
              'ai_prefix': ""}
        
        result = self.graph.invoke(dummy_input)

        return result

    def run(self):
        result = self._run()
        history = result['history']
        validation_input = [SystemMessage(self.output_prompt), HumanMessage(f'대화 내용 : {history}')]
        output = self.valid_gpt_output.invoke(validation_input)
        return output
    