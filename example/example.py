"""
Example script demonstrating how to use the Template Generator
"""
import os
import sys
import json

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ..generators.template_generator import TemplateGenerator

def example_usage():
    """Demonstrate various ways to use the template generator."""
    
    # Sample content (you can also load from file)
    sample_content = """
    qr code

OUT_OF_SCOPE

<!-- image -->

logo

OUT_OF_SCOPE

<!-- image -->

ﺗﻘﺪم ﻓﻲ أﻗﺴﺎم اﻟﻤﺪ أﻧﻪ ﻗﺴﻤﺎن: أﺻﻠﻲ وﻓﺮﻋﻲ، أﻣﺎ اﻟﻘﺴﻢ اﻷول ﻓﻘﺪ اﺳﺘﺒﺎن ﻟﻚ ﻓﻲ اﻟﺪرس اﻟﺴﺎﺑﻖ، وأﻣﺎ اﻟﻘﺴﻢ اﻟﺜﺎﻧﻲ ـ وﻫﻮ اﻟﻔﺮﻋﻲ ـ ﻓﻬﻮ أﻧﻮاع، أوﻟﻬﺎ اﻟﻤﺪ اﻟﻤﺘﺼﻞ.

remote sensing

OUT_OF_SCOPE

<!-- image -->

تعريف المد المتصل

. ﺣﺮف ﻣﺪ أﺗﻰ ﺑﻌﺪه ﻫﻤﺰ ﻣﺘﺼﻞ ﺑﻪ ﻓﻲ ﻛﻠﻤﺔ واﺣﺪة : اﻟﻤﺪ اﻟﻤﺘﺼﻞ ﻫﻮ

ﻓﺴﺒﺐ اﻟﻤﺪ ﻫﻮ اﻟﻬﻤﺰ اﻵﺗﻲ ﺑﻌﺪ ﺣﺮف اﻟﻤﺪ، وﻟﻬﺬا ﺳﻤﻲ )اﻟﻤﺪ اﻟﻤﺘﺼﻞ(؛ ﻻﺗﺼﺎل اﻟﻬﻤﺰ ﺑﺤﺮف اﻟﻤﺪ ﻓﻲ . ( ) و ( ) : ﻛﻠﻤﺔ واﺣﺪة، ﻣﺜﻞ

other

OUT_OF_SCOPE

<!-- image -->

حکه 4

ﻋﻨﺪ ﺟﻤﻴﻊ اﻟﻘﺮاء. اﻟﻮﺟﻮب : ﺣﻜﻢ اﻟﻤﺪ اﻟﻤﺘﺼﻞ .( وﻟﻬﺬا ﻳﺴﻤﻰ ﺑـ )اﻟﻤﺪ اﻟﻮاﺟﺐ

logo

OUT_OF_SCOPE

<!-- image -->

ﻓﻔﻴﻪ وﺟﻪ آﺧﺮ: وﻫﻮ اﻹﺷﺒﺎع ( j ) : ﻣﻘﺪار ﻣﺪه: اﻟﺘﻮﺳﻂ أرﺑﻊ ﺣﺮﻛﺎت، إﻻ إذا ﻛﺎﻧﺖ ﻫﻤﺰﺗﻪ ﻣﺘﻄﺮﻓﺔ ﻣﺜﻞ ﺳﺖ ﺣﺮﻛﺎت؛ ﻷﺟﻞ اﻟﻮﻗﻒ.

logo

OUT_OF_SCOPE

<!-- image -->

other

OUT_OF_SCOPE

<!-- image -->

ً

| اﻟﺘﻮﺿﻴﺢ                                                                                           | اﻟﻤﺪ ﺣﺮف   | اﻟﻤﺘﺼﻞ اﻟﻤﺪ اﻟﻜﻠﻤﺔ ﻃﺮف   | اﻟﻤﺘﺼﻞ اﻟﻤﺪ اﻟﻜﻠﻤﺔ وﺳﻂ   |   م |
|---------------------------------------------------------------------------------------------------|------------|--------------------------|--------------------------|-----|
| ﺟﺎء اﻟﻤﺪ ﺳﺒﺐ ﻫﻮ اﻟﺬي اﻟﻬﻤﺰ أن اﻷﻣﺜﻠﺔ ﻫﺬﻩ ﻓﻲ ﻧﺠﺪ                                                   | اﻷﻟﻒ       | ( )                      | ( )                      |   ١ |
| واﻟﻴﺎء؛ واﻟﻮاو اﻷﻟﻒ وﻫﻲ اﻟﺜﻼﺛﺔ، اﻟﻤﺪ ﺑﺤﺮوف ﻣﺘﺼﻼً ﻓﻲ اﻟﻬﻤﺰ ﻛﺎن إذا ﺣﺮﻛﺎت أرﺑﻊ ﺑﻤﻘﺪار ﻣﺪﻫﺎ وﺟﺐ وﻟﺬا | اﻟﻮاو      | ( )                      | ( )                      |   ٢ |
| وﺻﻼ ﻓﻴﻤﺪ ﻃﺮﻓﻬﺎ ﻓﻲ اﻟﻬﻤﺰ ﻛﺎن إذا وأﻣﺎ اﻟﻜﻠﻤﺔ، وﺳﻂ ﺣﺮﻛﺎت. أوﺳﺖ أرﺑﻊ ﺎ وﻗﻔً وﻳﻤﺪ ﺣﺮﻛﺎت، أرﺑﻊ         | اﻟﻴﺎء      | ( )                      | ( )                      |   ٣ |

الشاهد

قال الشيخ سليمان الجَمْزوري (١١):

other

OUT_OF_SCOPE

<!-- image -->

ﹾ

ﹼ

ﻳ ﹸ ﻌ ﹶ ﺪ ﹺ ﻞ ﹾ ا ﺑ ﹺ ﻤ ﹸ ﺘﱠﺼ ﹶ ذ ﹴ  و ﹶ ﺔ ﻠ ﹾ ﻤ ﻓ ﹺ ﻲ ﻛ

ﹶ

ﹺ

ﹾ

ﹼ

ﹾ ﺪ ﹶ  ﻣ ﹶ ﺪ ﹾ ﺰ ﹲ  ﺑ ﹶﻌ ﺎء ﹶ  ﻫ ﹶ ﻤ إ ﹺ ن ﹾ  ﺟ ﻓ ﹶ ﻮ ﹶ اﺟ ﹺﺐ

ﹶ

ﹲ

logo

OUT_OF_SCOPE

<!-- image -->

other

OUT_OF_SCOPE

<!-- image -->

أﻗﺮأ اﻵﻳﺘﻴﻦ اﻵﺗﻴﺘﻴﻦ، وأﺳﺘﺨﺮج ﻣﻨﻬﻤﺎ اﻟﻤﺪ اﻟﻤﺘﺼﻞ، ﻣﺒﻴ ﱢ ﻨ ً ﺎ ﺣﻜﻤﻪ وﻣﻘﺪارﻩ وﺳﺒﺒﻪ: : ﻗﺎل ﺗﻌﺎﻟﻰ: . )١( 9

| ﺳﺒﺒﻪ   | ﻣﻘﺪارﻩ   | ﺣﻜﻤﻪ   | اﻟﻤﺪ ﺣﺮف   | اﻟﻜﻠﻤﺔ   |   م |
|--------|----------|--------|------------|----------|-----|
|        |          |        |            |          |   ١ |
|        |          |        |            |          |   ٢ |
|        |          |        |            |          |   ٣ |
|        |          |        |            |          |   ٤ |
|        |          |        |            |          |   ٥ |
|        |          |        |            |          |   ٦ |

أﻋﻄﻲ ﻟﻜﻞ ﺣﺮف ﻣﻦ ﺣﺮوف اﻟﻤﺪ ﻣﺜﺎﻟﻴﻦ ﻓﻴﻬﻤﺎ ﻣﺪ ﻣﺘﺼﻞ، ﻣﺒﻴﻨ ً ﺎ ﺣﻜﻤﻪ وﻣﻘﺪارﻩ:

other

OUT_OF_SCOPE

<!-- image -->

| ﻣﻘﺪارﻩ   | اﻟﻤﺪ ﺣﻜﻢ   | اﻟﻤﺪ ﺣﺮف   |   م |
|----------|------------|------------|-----|
|          |            | اﻷﻟﻒ       |   ١ |
|          |            | اﻟﻮاو      |   ٢ |
|          |            | اﻟﻴﺎء      |   ٣ |
|          |            | اﻟﻴﺎء      |   ٣ |

logo

OUT_OF_SCOPE

<!-- image -->

.( )١( اﻷﺣﺰاب )٥٥-٦٥



ﻧﺸﺎط

أﺿﻊ داﺋﺮة ﺣﻮل اﻹﺟﺎﺑﺔ اﻟﺼﺤﻴﺤﺔ ﻣﻤﺎ ﻳﺄﺗﻲ:

ﺗﻤﺪ ﺑﻤﻘﺪار :

( ) )أرﺑﻊ أو ﺳﺖ ﺣﺮﻛﺎت( )ﺳﺖ ﺣﺮﻛﺎت( )أرﺑﻊ ﺣﺮﻛﺎت( )ﺣﺮﻛﺘﻴﻦ(

أ ـ ﻛﻠﻤﺔ

: ﻋﻨﺪ اﻟﻮﻗﻒ ﻋﻠﻴﻬﺎ ﺗﻤﺪ ﺑﻤﻘﺪار ( ) ب ـ ﻛﻠﻤﺔ )أرﺑﻊ أو ﺳﺖ ﺣﺮﻛﺎت( )ﺳﺖ ﺣﺮﻛﺎت( )أرﺑﻊ ﺣﺮﻛﺎت( )ﺣﺮﻛﺘﻴﻦ(

ﻓﻲ ﺣﺎﻟﺔ اﻟﻮﺻﻞ ﺗﻤﺪ ﺑﻤﻘﺪار : ( ) ج ـ ﻛﻠﻤﺔ )أرﺑﻊ أو ﺳﺖ ﺣﺮﻛﺎت( )ﺳﺖ ﺣﺮﻛﺎت( )أرﺑﻊ ﺣﺮﻛﺎت( )ﺣﺮﻛﺘﻴﻦ(

logo

OUT_OF_SCOPE

<!-- image -->

أوﻻً: اﻟﺘﻄﺒﻴﻖ ﻋﻠﻰ ﻛﻠﻤﺎت ﻣﻔﺮدة :

: ﻳﻘﺮأ ﻛﻞ ﻃﺎﻟﺐ اﻟﻜﻠﻤﺎت اﻵﺗﻴﺔ ﻣﻄﺒﻘ ًﺎ اﻟﻤﺪ اﻟﻤﺘﺼﻞ

other

OUT_OF_SCOPE

<!-- image -->

وورآبهم

## ً ﺎ: اﻟﺘﻄﺒﻴﻖ ﻋﻠﻰ اﻵﻳﺎت : ﺛﺎﻧﻴ

ﻳﻘﺮأ اﻟﻄﻼب اﻵﻳﺎت اﻵﺗﻴﺔ ﻣﻄﺒﻘﻴﻦ اﻟﻤﺪ اﻟﻤﺘﺼﻞ، ﻣﻊ ﻣﺮاﻋﺎة ﻣﺪ اﻟﺤﺮف اﻟﺬي ﺑﻌﺪﻩ ﻫﻤﺰة ﻓﻲ وﺳﻂ اﻟﻜﻠﻤﺔ ﺑﻤﻘﺪار أرﺑﻊ ﺣﺮﻛﺎت ﻓﻘﻂ، واﻟﺬي ﺑﻌﺪﻩ ﻫﻤﺰة ﻣﺘﻄﺮﻓﺔ ﺑﺎﻟﻮﺟﻬﻴﻦ: اﻟﺘﻮﺳﻂ أرﺑﻊ ﺣﺮﻛﺎت، واﻹﺷﺒﺎع ﺳﺖ ﺣﺮﻛﺎت .

logo

OUT_OF_SCOPE

<!-- image -->

: ﻗﺎل  ﺗﻌﺎﻟﻰ: . ( )١ 9 ١٦٢ ١٦٣ من والسحاب وتصريف آلبحر دآبة

screenshot

OUT_OF_SCOPE

<!-- image -->

)١( ﻋﺮ ﱢ ف اﻟﻤﺪ اﻟﻤﺘﺼﻞ. )٢( ﻣﺎ ﺣﻜﻢ اﻟﻤﺪ اﻟﻤﺘﺼﻞ؟ وﻣﺎ ﻣﻘﺪار ﻣﺪ ﹼ ه؟ )٣( اﻗﺮأ اﻵﻳﺎت اﻟﻜﺮﻳﻤﺔ اﻵﺗﻴﺔ ﺟﻬﺮ ﹰ ا، ﺛﻢ اﺳﺘﺨﺮج اﻟﻤﺪ اﻟﻤﺘﺼﻞ، وﺑ ﹶ ـﻴ ﱢ ﻦ ﺣﻜﻤﻪ، وﻣﻘﺪار ﻣ ﹶ ﺪ ﱢ ه: : : ١ــ  ﻗﺎل  ﺗﻌﺎﻟﻰ . ( )٢ 9 : : ٢ــ ﻗﺎل ﺗﻌﺎﻟﻰ . ( )٣ 9 . ( )٤ 9 : : ٣ــ ﻗﺎل ﺗﻌﺎﻟﻰ

)٤( ﺳﺠ ﱢ ﻞ ﻣﻦ ﺣﻔﻈﻚ ﺛﻼﺛﺔ أﻣﺜﻠﺔ ﻟﻠﻤﺪ اﻟﻤﺘﺼﻞ ﻣﺒﻴﻨﹰﺎ ﺣﻜﻤﻪ وﻣﻘﺪار ﻣ ﹶ ﺪ ﱢ ه.

.( )١( اﻟﺒﻘﺮة )١٦١-٤٦١

logo

OUT_OF_SCOPE

<!-- image -->

## معلومات إثرائية

للمد المتصل عدة أسماء، منها: (مد النُّنَّة)؛ لأن الكلمة فيها بنيت على المد، ويسمى بـ(المد المُمكن)؛ لأن القارئ لا يتمكن من تحقيق الهمزة تحقيقًا محكمًا إلا به، ويسمى بـ(مد الكلمة)؛ لأن حرف المد والهمزة في كلمة واحدة.

◄ قال الإمام ابن الجزري ٨٨ في كتابه النشر في القراءات العشر في قصر المد المتصل: (وقد تتبعته فلم أجده في قراءة صحيحة ولا شاذة)(١).

)١( اﻟﻨﺸﺮ ﻓﻲ اﻟﻘﺮءات اﻟﻌﺸﺮ، ﺷﻤﺲ اﻟﺪﻳﻦ ﻣﺤﻤﺪ ﺑﻦ اﳉﺰري ج ١ ص ٥١٣.

logo

OUT_OF_SCOPE

<!-- image -->
    """
    
    # Learning goals
    sample_goals = [
        "ﻳﻘﺮأ ﻛﻞ ﻃﺎﻟﺐ اﻟﻜﻠﻤﺎت اﻵﺗﻴﺔ ﻣﻄﺒﻘ ًﺎ اﻟﻤﺪ اﻟﻤﺘﺼﻞ"
    ]
    
    print("🚀 Template Generator Example")
    print("=" * 40)
    
    try:
        # Initialize generator
        generator = TemplateGenerator()
        
        # Example 1: Generate Goal-Based Question Bank
        print("\n📝 Generating Goal-Based Question Bank...")
        questions = generator.generate_goal_based_questions(
            content=sample_content,
            goals=sample_goals,
            question_counts={
                "multiple_choice": 2,
                "short_answer": 2,
                "complete": 2,
                "true_false": 2
            },
            difficulty_levels=[1, 2]
        )
        
        print("✅ Goal-Based Question Bank Generated!")
        
        # Print detailed information about the goal-based results
        if '_goal_based_metadata' in questions:
            metadata = questions['_goal_based_metadata']
            print(f"   Total Goals: {metadata['total_goals']}")
            print(f"   Total Questions: {metadata['total_questions']}")
            print(f"   Questions per Goal: {metadata['questions_per_goal_distribution']}")
        
        print(f"   Multiple Choice: {len(questions['multiple_choice'])}")
        print(f"   Short Answer: {len(questions['short_answer'])}")
        print(f"   Complete: {len(questions['complete'])}")
        print(f"   True/False: {len(questions['true_false'])}")
        
        # Show goal-question mapping
        if 'goal_question_mapping' in questions:
            print("\n🎯 Goal-Question Mapping:")
            for mapping in questions['goal_question_mapping']:
                print(f"   • {mapping['goal_text'][:50]}... -> {mapping['question_count']} questions")
                types = mapping['question_types']
                print(f"     MC: {types['multiple_choice']}, SA: {types['short_answer']}, "
                      f"Comp: {types['complete']}, TF: {types['true_false']}")
        
        # Example 2: Generate Worksheet
        print("\n📋 Generating Worksheet...")
        worksheet = generator.generate_worksheet(
            content=sample_content,
            goals=sample_goals
        )
        
        print("✅ Worksheet Generated!")
        print(f"   Goals: {len(worksheet['goals'])}")
        print(f"   Applications: {len(worksheet['applications'])}")
        print(f"   Vocabulary: {len(worksheet['vocabulary'])}")
        print(f"   Guidelines: {len(worksheet['teacher_guidelines'])}")
        
        # Example 3: Generate Summary
        print("\n📄 Generating Summary...")
        summary = generator.generate_summary(content=sample_content)
        
        print("✅ Summary Generated!")
        print(f"   Opening: {summary['opening'][:50]}...")
        print(f"   Summary: {summary['summary'][:50]}...")
        print(f"   Ending: {summary['ending'][:50]}...")
        
        # Example 4: Generate Mind Map (NEW!)
        print("\n🧠 Generating Mind Map...")
        mindmap = generator.generate_mindmap(content=sample_content)
        
        print("✅ Mind Map Generated!")
        print(f"   Nodes: {len(mindmap.get('nodeDataArray', []))}")
        print(f"   Model Class: {mindmap.get('class', 'N/A')}")
        if mindmap.get('nodeDataArray'):
            root_node = next((node for node in mindmap['nodeDataArray'] if node.get('parent') is None), {})
            print(f"   Root Topic: {root_node.get('text', 'N/A')}")
            main_branches = [node for node in mindmap['nodeDataArray'] if node.get('parent') == root_node.get('key', 0)]
            print(f"   Main Branches: {len(main_branches)}")
        
        # Save examples to files
        print("\n💾 Saving examples to files...")
        
        with open("example_questions.json", "w", encoding="utf-8") as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)
        
        with open("example_worksheet.json", "w", encoding="utf-8") as f:
            json.dump(worksheet, f, ensure_ascii=False, indent=2)
        
        with open("example_summary.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        with open("example_mindmap.json", "w", encoding="utf-8") as f:
            json.dump(mindmap, f, ensure_ascii=False, indent=2)
        
        with open("example_summary.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        with open("example_mindmap.json", "w", encoding="utf-8") as f:
            json.dump(mindmap, f, ensure_ascii=False, indent=2)
        
        print("✅ Examples saved successfully!")
        print("   - example_questions.json")
        print("   - example_worksheet.json") 
        print("   - example_summary.json")
        print("   - example_mindmap.json")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\n💡 Make sure to:")
        print("   1. Install requirements: pip install -r requirements.txt")
        print("   2. Set your OPENAI_API_KEY environment variable")
        print("   3. Check your internet connection")

if __name__ == "__main__":
    example_usage()
