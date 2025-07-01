import asyncio
from schemas.ConversationState import ConversationState
from schemas.ValidationResponse import ValidationResponse
from schemas.ElderlyUser import ElderlyUser
import yaml
from dotenv import load_dotenv
import os

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langchain.schema.messages import HumanMessage, SystemMessage
from VoiceToText import VoiceToText
from client import TwilioClient # TwilioClient 임포트

class conversation_logic:
    # __init__에서 TwilioClient 인스턴스를 인자로 받도록 변경
    def __init__(self, call_sid: str, client_instance: TwilioClient):
        question_config = yaml.safe_load(open('./configs/essential_question_prompts.yaml', 'r', encoding='utf-8'))
        validation_config = yaml.safe_load(open('./configs/validation_prompts.yaml', 'r', encoding='utf-8'))
        output_config = yaml.safe_load(open('./configs/output_format_prompt.yaml', 'r', encoding='utf-8'))
        load_dotenv()
        # server_base_url은 client_instance가 이미 가지고 있으므로 여기서 필요 없습니다.
        
        # 주입받은 TwilioClient 인스턴스를 사용합니다.
        self.client = client_instance 
        self.call_sid = call_sid

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

    async def initialize(self, state: ConversationState) -> ConversationState:
        print('initialize start')
        call_sid = state['call_sid']
        await self.client.say(call_sid, "안녕하세요. 어르신의 구직을 도와드리기 위해 몇 가지 질문을 드리겠습니다.")
        await asyncio.sleep(1) 
        await self.client.say(call_sid, "질문에 대한 답변은 가능한 구체적으로 말씀해주실 수록 최적의 구직 정보를 제공받으실 수 있습니다.")
        await asyncio.sleep(1)
        await self.client.say(call_sid, "그럼 시작하겠습니다.")
        await asyncio.sleep(1)

        return state

    async def conversation(self, state: ConversationState) -> ConversationState:
        phase = state['phase']
        call_sid = state['call_sid']
        AIquestion = self.question_list[phase]
 
        # TTS로 질문 음성 출력
        await self.client.say(call_sid, AIquestion) 

        # STT로 사용자의 답변 음성 입력
        wav_file_path = await self.client.listen(call_sid, phase = phase)
        print('오디오 경로 :', wav_file_path)
        human_answer = None
        if wav_file_path: # wav_file_path가 있을 때만 STT 실행
            # vtt.listen()이 블로킹 작업일 수 있으므로 asyncio.to_thread로 감싸서 실행합니다.
            human_answer = await asyncio.to_thread(self.vtt.listen, wav_file_path)

        # 녹음 실패 또는 STT 실패 시
        if human_answer is None or "[녹음 실패]" in human_answer or "[녹음된 음성이 없습니다]" in human_answer:
            await self.client.say(call_sid, "죄송합니다. 음성이 잘 들리지 않았어요. 다시 한 번 천천히 말씀해주시겠어요?")
            return await self.retry(state) # retry가 async이므로 await

        # 정상 응답 처리
        print(f"[USER] {human_answer}")
        past_history = state['history']
        new_history = past_history + [f"AI : {AIquestion}\n",]
        new_history = new_history + [f"User : {human_answer}\n"]

        return {'history' : new_history, 'last_response': human_answer }

    async def is_valid(self, state: ConversationState) -> str:
        phase = state['phase']
        call_sid = state['call_sid']
        AIquestion = self.question_list[phase]
        validation_prompt = self.validation_list[phase]
        human_answer = state['last_response']

        validation_input = [SystemMessage(validation_prompt), HumanMessage(f'질문: {AIquestion} \n답변: {human_answer}')]
        # LangChain의 invoke 메서드가 비동기라면 ainvoke 사용
        justification = await self.valid_gpt.ainvoke(validation_input)
        
        if justification.is_valid:
            if state['phase'] == len(self.question_list) - 1:
                await self.client.say(call_sid, "모든 질문에 대한 답변이 끝나셨습니다. 어르신의 답변을 바탕으로 최적의 구직 정보를 빠른 시일 내에 메세지로 전달해드리겠습니다. 감사합니다.")
                return "End"
            else:
                return  "Next" # 'Next'로 반환하고, before_next에서 실제로 phase를 증가시킵니다.
        else:
            common_prefix = '어르신, 말씀주신 내용이 충분하지 않은 것 같아요.'
            ai_prefix = justification.message
            text = f"{common_prefix} {ai_prefix}"
            await self.client.say(call_sid, text)
            return "Retry"
        
    async def before_next(self, state: ConversationState) -> ConversationState:
        call_sid = state['call_sid']
        await self.client.say(call_sid, "감사합니다. 다음 질문으로 넘어가겠습니다.")
        
        return {'phase': state['phase'] + 1,}

    async def before_end(self, state: ConversationState) -> ConversationState:
        call_sid = state['call_sid']
        await self.client.say(call_sid, "어르신, 대화가 종료되었습니다.")
        await self.client.hangup(call_sid) 
        return {'history': state['history'] + [f"[대화 종료]"],}
      

    async def retry(self, state: ConversationState) -> ConversationState:
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
        graph.recursion_limit = 200
        self.graph = graph

    async def _run(self):
        # compose_workflow()는 __init__에서 이미 호출되었으므로 여기서 다시 호출할 필요 없습니다.
        dummy_input = {'phase': 0,
              'history': [],
              'last_response': "",
              'ai_prefix': "",
              'call_sid' : self.call_sid}
        
        result = await self.graph.ainvoke(dummy_input)

        return result

    async def run(self):
        result = await self._run()
        history = result['history']
        validation_input = [SystemMessage(self.output_prompt), HumanMessage(f'대화 내용 : {history}')]

        
        # LangChain의 invoke 메서드가 비동기라면 ainvoke 사용
        output = await self.valid_gpt_output.ainvoke(validation_input)
# Sample
# INFO:     54.209.203.118:59782 - "POST /voice HTTP/1.1" 200 OK
# 최종 output: {'name': '김영종', 'age': 76, 'location': '경기도 용인시 수지구',
# 'available_time': '오전 9시부터 오후 6시까지', 'license': '환경 미화원 자격증', 
# 'preferred_field': '청소', 'health_condition': '다리가 조금 아픕니다', 
# 'career': '어렸을 때부터 청소 일을 했고, 삼성 아파트에서 청소원으로 근무했다',
#  'education': '낙생 초등학교, 낙원 중학교, 낙생 고등학교 졸업; 대학교는 졸업하지 않음'}

        return output