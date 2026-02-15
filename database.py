import random

QUESTIONS = [
    {"type":"true_false","question":"التخطيط هو أول وظائف الإدارة","answer":True},
    {"type":"true_false","question":"التنظيم يأتي قبل التخطيط","answer":False},
    {"type":"multiple_choice","question":"من وظائف الإدارة الأساسية؟",
     "options":["التخطيط","التنظيم","التوجيه","كل ما سبق"],"answer":3},
    {"type":"multiple_choice","question":"أي مما يلي يعد من عناصر القيادة؟",
     "options":["التأثير","الاتصال","التحفيز","جميعها"],"answer":3},
    {"type":"fill_blank","question":"تعرف الإدارة بأنها تحقيق الأهداف باستخدام ____ المتاحة","answer":"الموارد"},
]

def get_questions(n):
    return random.sample(QUESTIONS, min(n,len(QUESTIONS)))