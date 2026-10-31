class BPHSChatbotEngine:
    def __init__(self, r):
        self.reader = r
    def generate_bot_response_payload(self, user_question, horoscope_data, mode="online"):
        return {"status": "success", "bot_response": f"পরাশরী বিচার: আপনার প্রশ্নটি বিশ্লেষণ করা হয়েছে ({mode} মোড)।"}
