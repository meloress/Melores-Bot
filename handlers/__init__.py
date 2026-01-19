from aiogram import Dispatcher
from .admins.media_setup import router as media_router
from .admin.statistics import router as statistics_router
from .admin.panel import router as panel_router
from .users.start import router as start_router
from .users.lessons import router as lessons_router
from .users.remont import router as remont_router
from .users.about import router as about_router
from .users.zamer import router as zamer_router
from .users.questions import router as questions_router
from .users.contact import router as contact_router
from .admin.crm import router as crm_router
from .admin.mailing import router as mailing_router
from .admin.admins_management import router as admin_manage_router

def register_all_handlers(dp: Dispatcher):
    # Admin handlerlar
    dp.include_router(media_router)
    dp.include_router(statistics_router) 
    dp.include_router(panel_router)
    dp.include_router(crm_router)
    dp.include_router(mailing_router)
    dp.include_router(admin_manage_router)\
    
    # User handlerlar
    dp.include_router(start_router)
    dp.include_router(lessons_router)
    dp.include_router(remont_router)
    dp.include_router(about_router)
    dp.include_router(zamer_router)
    dp.include_router(questions_router)
    dp.include_router(contact_router)
    
    
    from aiogram import Dispatcher

