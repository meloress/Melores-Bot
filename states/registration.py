from aiogram.fsm.state import StatesGroup, State

class RegisterState(StatesGroup):
    fullname = State()  
    phone = State()     
    region = State()    

class QuestionState(StatesGroup):
    waiting_question = State() 

class ZamerState(StatesGroup):
    fullname = State() 
    phone = State()    
   
class AdminCrmState(StatesGroup):
    search_id = State()     
    search_phone = State()  
    search_username = State()
    send_personal_msg = State()  
 
class AdminMailingState(StatesGroup):
    selection = State() 
    msg_content = State()
    private_id = State()
    save_template_name = State()    

class AdminManageState(StatesGroup):
    add_new_admin_id = State() 