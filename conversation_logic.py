
from schemas.ConversationState import ConversationState
from schemas.ValidationResponse import ValidationResponse
import yaml
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langchain.schema.messages import HumanMessage, SystemMessage
from langchain.schema.messages import HumanMessage
## TODO: import Voice2Text

class conversation_logic:
    def __init__(self):
        question_config = yaml.safe_load(open('./configs/essential_question_prompts.yaml', 'r', encoding='utf-8'))
        validation_config = yaml.safe_load(open('./configs/validation_prompts.yaml', 'r', encoding='utf-8'))
        load_dotenv()

        self.question_list = [question_config['essential_question1'], 
                        question_config['essential_question2'],
                        question_config['essential_question3'],
                        question_config['essential_question4'],
                        question_config['essential_question5']]


        self.validation_list = [validation_config['validation_question1'],
                        validation_config['validation_question1'],
                        validation_config['validation_question1'],
                        validation_config['validation_question1'],
                        validation_config['validation_question1']]
        
        self.gpt = ChatOpenAI(model="gpt-4o-mini",)
        self.valid_gpt = self.gpt.with_structured_output(ValidationResponse)

#  ---------------------------NODES-----------------------------------------------------

    def initialize(self, state: ConversationState) -> ConversationState:
        ## TODO : Voice2Text.speak 부분은 음성으로 음성으로 들을 수 있도록 구현
        # Voice2Text.speak("안녕하세요. 어르신의 구직을 도와드리기 위해 몇 가지 질문을 드리겠습니다.")
        # Voice2Text.speak("질문에 대한 답변은 가능한 구체적으로 말씀해주실 수록 최적의 구직 정보를 제공받으실 수 있습니다.")
        # Voice2Text.speak("그럼 시작하겠습니다.")
        print("안녕하세요. 어르신의 구직을 도와드리기 위해 몇 가지 질문을 드리겠습니다.")
        print("질문에 대한 답변은 가능한 구체적으로 말씀해주실 수록 최적의 구직 정보를 제공받으실 수 있습니다.")
        print("그럼 시작하겠습니다.")

        return state

    def conversation(self, state: ConversationState) -> ConversationState:
        phase = state['phase']
        AIquestion = self.question_list[phase]
        ## TODO: AI 질문을 음성으로 사용자에게 전달 후 그 대답을 Text로 받아오기
        ## Voice2Text.listen 사용자의 답을 음성으로 받아 Text로 변환

        # Voice2Text.speak(AIquestion)
        print(AIquestion)

        # human_answer = Voice2Text.listen()
        human_answer = input("어르신의 답변: ")
        
        print(f"어르신의 답변: {human_answer}")
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
                # Voice2Text.speak("모든 질문에 대한 답변이 끝나셨습니다. \
                #                  어르신의 답변을 바탕으로 최적의 구직 정보를 빠른 시일 내에 메세지로 전달해드리겠습니다. \
                #                  감사합니다.")
                print("모든 질문에 대한 답변이 끝나셨습니다. " \
                        "어르신의 답변을 바탕으로 최적의 구직 정보를 빠른 시일 내에 메세지로 전달해드리겠습니다." \
                        "감사합니다.")
                return "End"
            else:
                state['phase'] += 1
                return  "Next"
        else:
            common_prefix = '어르신, 말씀주신 내용이 충분하지 않은 것 같아요.'
            ai_prefix = justification.message
            ## TODO: AI가 판단하기에 부족한 부분을 음성으로 전달하기

            # Voice2Text.speak(f"{common_prefix} {aiprefix}")
            print(f"{common_prefix} {ai_prefix}")
            return "Retry"
        
    def before_next(self, state: ConversationState) -> ConversationState:
        # Voice2Text.speak("어르신, 다음 질문으로 넘어가겠습니다.")
        print("감사합니다 어르신. 그럼 다음 질문으로 넘어가겠습니다.")
        
        return {'phase': state['phase'] + 1,}

    def before_end(self, state: ConversationState) -> ConversationState:
        # Voice2Text.speak("어르신, 대화가 종료되었습니다.")
        print("어르신, 대화가 종료되었습니다.")
        
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

    def run(self):
        self.compose_workflow()
        dummy_input = {'phase': 0,
              'history': [],
              'last_response': "",
              'ai_prefix': ""}
        
        result = self.graph.invoke(dummy_input)

        return result
