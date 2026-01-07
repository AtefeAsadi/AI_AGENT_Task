import json
from typing import Dict, Any, Tuple

# 1. تعریف حافظه مشترک: این دیکشنری مرجع اصلی ما برای هویت کاراکترهاست.
SHARED_MEMORY: Dict[str, Dict[str, str]] = {
    "Kaveh": {
        "hair_color": "مشکی",
        "outfit": "زره آبی سنگین",  # این جزئیات نباید تغییر کنند
        "weapon": "شمشیر طلایی"
    }
}

# 2. ورودی داستان: لیست صحنه‌هایی که Agent باید پردازش کند.
# **نکته مهم:** صحنه دوم شامل یک "تناقض" (لباس قرمز) است تا منطق Agent Checker تست شود.
STORY_SEGMENTS: list[Dict[str, Any]] = [
    {
        "Scene_ID": 1,
        "Character": "Kaveh",
        "Text": "کاوه وارد شهر شد و با شمشیر طلایی خود در میدان مبارزه کرد."
    },
    {
        "Scene_ID": 2,
        "Character": "Kaveh",
        "Text": "سپس کاوه به سمت کوهستان برفی رفت. او در آنجا لباسی به رنگ قرمز به تن داشت و منتظر بود." 
    }
]

ALL_SCENES_OUTPUT: list[Dict[str, Any]] = []

class ConsistencyCheckerAgent:
    """
    Agent بررسی ثبات (Checker Agent).
    وظیفه: اجرای قوانین ثبات و حفاظت از هویت کاراکتر.
    """
    def __init__(self, shared_memory: Dict[str, Dict[str, str]]):
        self.memory = shared_memory

    def check_and_enforce(self, character_name: str, input_text: str) -> Tuple[str, str]:
        """
        اینجا Agent ما متن داستان را با حافظه مشترک مقایسه می‌کند تا تضادها را پیدا کند.
        """
        
        char_memory = self.memory.get(character_name, {})
        
        # توصیف ثابت کاراکتر
        consistent_desc = f"رنگ مو: {char_memory.get('hair_color')}, لباس: {char_memory.get('outfit')}, سلاح: {char_memory.get('weapon')}"
        
        is_conflict = False
        
        # --- منطق تشخیص تضاد (اجرای گام اول تأییدیه) ---
        # تست می‌کنیم که آیا متن، رنگ لباس ثابت کاراکتر را عوض کرده است؟
        if "قرمز" در input_text or "قرمزی" در input_text:
            if char_memory.get('outfit') == "زره آبی سنگین":
                is_conflict = True
        
        # --- تصمیم‌گیری: اجرای منطق صرفه‌جویی ---
        # اگر تضاد پیدا شد، سیستم اصلاح می‌کند (اجبار به ثبات) و از تولید پرامپت غلط (هزینه بیهوده) جلوگیری می‌کند.
        
        if is_conflict:
            print(f"⚠️ هشدار تضاد! برای {character_name}: متن با حافظه تضاد دارد. (لباس قرمز در مقابل آبی)")
            print(f"✅ انتخاب شد: توصیف ثابت (Consistency Enforced) - جلوی هزینه بیهوده گرفته شد.")
            return consistent_desc, "Enforced"
        else:
            return consistent_desc, "Consistent"

class SceneGeneratorAgent:
    """
    Agent تولید صحنه.
    وظیفه: تولید پرامپت نهایی برای مدل‌های تولید ویدیو، پس از دریافت تأییدیه ثبات.
    """
    def __init__(self, checker_agent: ConsistencyCheckerAgent):
        self.checker = checker_agent

    def generate_scene(self, scene_data: Dict[str, Any]) -> Dict[str, Any]:
        
        # 1. مراجعه به Agent بررسی ثبات (اجرای منطق تأییدیه)
        consistent_desc, status = self.checker.check_and_enforce(scene_data["Character"], scene_data["Text"])
        
        # 2. ساخت توصیف صحنه بر اساس اطلاعات ثابت
        if status == "Enforced":
             # اگر تضاد بود، Agent ناظر پرامپت را بر اساس حافظه ثابت اصلاح می‌کند.
             prompt_text = f"متن اصلی داستان: {scene_data['Text']}. (توجه: کاراکتر باید با توصیف ثابت: {consistent_desc} ظاهر شود.)"
        else:
             # در حالت عادی از متن داستان و توصیف ثابت استفاده می‌شود.
             prompt_text = f"متن اصلی داستان: {scene_data['Text']}. (توام با توصیف کاراکتر: {consistent_desc})."

        # خروجی نهایی به شکل JSON ساختاریافته (اجرای منطق JSON Schema)
        output_json = {
            "Scene_ID": scene_data["Scene_ID"],
            "Story_Segment": scene_data["Text"],
            "Consistency_Status": status,
            "Video_Generation_Prompt": prompt_text,
            "Used_Character_Attributes": consistent_desc
        }
        
        return output_json

# --- اجرای Orchestration ---
if __name__ == "__main__":
    
    # 1. راه‌اندازی Agentها
    checker = ConsistencyCheckerAgent(SHARED_MEMORY)
    generator = SceneGeneratorAgent(checker)

    print("--- شروع Orchestration و تست Edge Case ---")
    
    # 3. اجرای Agentها بر روی تمام بخش‌های داستان
    for segment in STORY_SEGMENTS:
        scene_output = generator.generate_scene(segment)
        ALL_SCENES_OUTPUT.append(scene_output)
        print(f"\n[صحنه {scene_output['Scene_ID']}]: وضعیت ثبات: {scene_output['Consistency_Status']}")
        print(f"توصیف استفاده شده: {scene_output['Used_Character_Attributes']}")
        
    print("\n--- خروجی نهایی (فایل JSON) در کنسول: ---")
    # خروجی به صورت JSON (برای ارتباط کدگونه Agentها)
    print(json.dumps(ALL_SCENES_OUTPUT, indent=2, ensure_ascii=False))
