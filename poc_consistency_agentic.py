import json
from typing import Dict, Any, Tuple

# 1. تعریف حافظه مشترک (Shared Memory)
# این حافظه جزئیات ثابت کاراکتر را نگه می‌دارد.
SHARED_MEMORY: Dict[str, Dict[str, str]] = {
    "Kaveh": {
        "hair_color": "مشکی",
        "outfit": "زره آبی سنگین",  # <-- جزئیات ثابت
        "weapon": "شمشیر طلایی"
    }
}

# 2. ورودی داستان
# در صحنه ۲، یک تناقض (لباس قرمز) وارد شده تا سیستم تست شود.
STORY_SEGMENTS: list[Dict[str, Any]] = [
    {
        "Scene_ID": 1,
        "Character": "Kaveh",
        "Text": "کاوه وارد شهر شد و با شمشیر طلایی خود در میدان مبارزه کرد."
    },
    {
        "Scene_ID": 2,
        "Character": "Kaveh",
        "Text": "سپس کاوه به سمت کوهستان برفی رفت. او در آنجا لباسی به رنگ قرمز به تن داشت و منتظر بود." # <-- تناقض
    }
]

ALL_SCENES_OUTPUT: list[Dict[str, Any]] = []

class ConsistencyCheckerAgent:
    """
    Agent بررسی ثبات (Checker Agent).
    وظیفه: مقایسه متن ورودی با حافظه مشترک و اجبار به ثبات.
    """
    def __init__(self, shared_memory: Dict[str, Dict[str, str]]):
        self.memory = shared_memory

    def check_and_enforce(self, character_name: str, input_text: str) -> Tuple[str, str]:
        """
        تضادها را پیدا می‌کند و توصیف ثابت را برمی‌گرداند.
        این تابع شبیه‌سازی منطق LLM برای بررسی تضاد است.
        """
        
        char_memory = self.memory.get(character_name, {})
        
        # ترکیب توصیف‌های ثابت برای استفاده در پرامپت تولید ویدیو
        consistent_desc = f"رنگ مو: {char_memory.get('hair_color')}, لباس: {char_memory.get('outfit')}, سلاح: {char_memory.get('weapon')}"
        
        is_conflict = False
        
        # --- شبیه‌سازی تشخیص تضاد (منطق تأییدیه) ---
        # بررسی می‌کنیم که آیا متن ورودی حاوی کلمه‌ای است که با حافظه تضاد دارد؟
        if "قرمز" در input_text or "قرمزی" در input_text:
            if char_memory.get('outfit') == "زره آبی سنگین":
                is_conflict = True
        
        # --- تصمیم‌گیری: اجرای منطق صرفه‌جویی (تأییدیه) ---
        # اگر تضاد بود، Agent اجازه نمی‌دهد خروجی با کیفیت پایین تولید شود.
        
        if is_conflict:
            print(f"⚠️ هشدار تضاد! برای {character_name}: متن با حافظه تضاد دارد. (لباس قرمز در مقابل آبی)")
            print(f"✅ انتخاب شد: توصیف ثابت (Consistency Enforced) - جلوگیری از هزینه بیهوده.")
            return consistent_desc, "Enforced"
        else:
            return consistent_desc, "Consistent"

class SceneGeneratorAgent:
    """
    Agent تولید صحنه.
    وظیفه: تولید پرامپت نهایی برای مدل‌های تولید ویدیو.
    """
    def __init__(self, checker_agent: ConsistencyCheckerAgent):
        self.checker = checker_agent

    def generate_scene(self, scene_data: Dict[str, Any]) -> Dict[str, Any]:
        character = scene_data["Character"]
        input_text = scene_data["Text"]
        scene_id = scene_data["Scene_ID"]
        
        # 1. مراجعه به Agent بررسی ثبات (اجرای منطق تأییدیه سه‌گانه)
        consistent_desc, status = self.checker.check_and_enforce(character, input_text)
        
        # 2. ساخت توصیف صحنه بر اساس اطلاعات ثابت
        if status == "Enforced":
             # اگر تضاد بود، پرامپت را بر اساس حافظه می‌سازیم و به مدل دستور می‌دهیم ثابت باشد.
             prompt_text = f"متن اصلی داستان: {input_text}. (توجه: کاراکتر باید با توصیف ثابت: {consistent_desc} ظاهر شود.)"
        else:
             # در حالت عادی از متن داستان و توصیف ثابت استفاده می‌شود.
             prompt_text = f"متن اصلی داستان: {input_text}. (توام با توصیف کاراکتر: {consistent_desc})."

        # خروجی نهایی به شکل JSON ساختاریافته (اجرای منطق JSON Schema)
        output_json = {
            "Scene_ID": scene_id,
            "Story_Segment": input_text,
            "Consistency_Status": status,
            "Video_Generation_Prompt": prompt_text,
            "Used_Character_Attributes": consistent_desc
        }
        
        return output_json

# --- اجرای Orchestration ---
if __name__ == "__main__":
    
    # 1. راه‌اندازی Agent بررسی ثبات
    checker = ConsistencyCheckerAgent(SHARED_MEMORY)

    # 2. راه‌اندازی Agent تولید صحنه
    generator = SceneGeneratorAgent(checker)

    print("--- شروع Orchestration و تست Edge Case ---")
    
    # 3. اجرای Agentها بر روی تمام بخش‌های داستان
    for segment in STORY_SEGMENTS:
        scene_output = generator.generate_scene(segment)
        ALL_SCENES_OUTPUT.append(scene_output)
        print(f"\n[صحنه {scene_output['Scene_ID']}]: وضعیت ثبات: {scene_output['Consistency_Status']}")
        print(f"توصیف استفاده شده: {scene_output['Used_Character_Attributes']}")
        
    print("\n--- خروجی نهایی (فایل JSON) در کنسول: ---")
    # خروجی به صورت JSON (ارتباط کدگونه)
    print(json.dumps(ALL_SCENES_OUTPUT, indent=2, ensure_ascii=False))
