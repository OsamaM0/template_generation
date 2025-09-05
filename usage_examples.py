#!/usr/bin/env python3
"""
Simple usage examples for Goal-Based Question Generation

This script shows how to use the new goal-based functionality in your code.
"""

from generators.template_generator import TemplateGenerator

def example_with_goals():
    """Example: Generate questions when goals are provided"""
    print("📋 Example 1: Goals Provided")
    print("-" * 40)
    
    # Your content
    content = """
الجبر - المعادلات الخطية
المعادلة الخطية هي معادلة من الدرجة الأولى تحتوي على متغير واحد أو أكثر.
الشكل العام للمعادلة الخطية في متغير واحد: أ س + ب = 0
حيث أ ≠ 0
مثال: 2س + 3 = 7
الحل: 2س = 7 - 3 = 4، إذن س = 2
"""
    
    # Your goals
    goals = [
        "يتعرف الطالب على شكل المعادلة الخطية",
        "يحل الطالب المعادلات الخطية البسيطة",
        "يتحقق الطالب من صحة الحل"
    ]
    
    # Generate goal-based questions
    generator = TemplateGenerator()
    result = generator.generate_goal_based_questions(
        content=content,
        goals=goals
    )
    
    # Display key information
    print(f"✅ Generated questions for {len(result['learning_goals'])} goals")
    print(f"📝 Total questions: {result['_goal_based_metadata']['total_questions']}")
    
    # Show goal-question mapping
    for mapping in result['goal_question_mapping']:
        print(f"🎯 {mapping['goal_text'][:50]}... → {mapping['question_count']} questions")
    
    return result

def example_without_goals():
    """Example: Generate questions when no goals are provided"""
    print("\n📋 Example 2: No Goals Provided")
    print("-" * 40)
    
    # Your content only
    content = """
الكيمياء - الذرة والعناصر
الذرة هي أصغر وحدة بناء في المادة تحتفظ بخصائص العنصر.
تتكون الذرة من نواة موجبة الشحنة محاطة بإلكترونات سالبة الشحنة.
النواة تحتوي على بروتونات وعادة نيوترونات.
العدد الذري للعنصر يساوي عدد البروتونات في النواة.
"""
    
    # Generate goal-based questions without goals
    generator = TemplateGenerator()
    result = generator.generate_goal_based_questions(
        content=content,
        goals=None  # No goals provided
    )
    
    # Display key information
    print(f"✅ System generated {len(result['learning_goals'])} goals automatically")
    print(f"📝 Total questions: {result['_goal_based_metadata']['total_questions']}")
    
    # Show generated goals
    print("🎯 Generated Goals:")
    for goal in result['learning_goals']:
        print(f"   • {goal['text']}")
    
    return result

def example_custom_question_counts():
    """Example: Custom question distribution"""
    print("\n📋 Example 3: Custom Question Distribution")
    print("-" * 40)
    
    content = """
اللغة العربية - النحو والإعراب
الإعراب هو تغيير أحوال أواخر الكلم لاختلاف العوامل الداخلة عليها.
علامات الإعراب الأصلية: الضمة للرفع، الفتحة للنصب، الكسرة للجر، السكون للجزم.
المبتدأ والخبر مرفوعان دائماً.
الفاعل مرفوع دائماً.
المفعول به منصوب دائماً.
"""
    
    goals = [
        "يتعرف الطالب على مفهوم الإعراب",
        "يميز الطالب علامات الإعراب الأصلية",
        "يطبق الطالب قواعد الإعراب على الأمثلة"
    ]
    
    # Custom question distribution
    generator = TemplateGenerator()
    result = generator.generate_goal_based_questions(
        content=content,
        goals=goals,
        question_counts={
            "multiple_choice": 8,    # More multiple choice
            "short_answer": 2,       # Fewer short answer
            "complete": 4,           # More completion
            "true_false": 2          # Fewer true/false
        }
    )
    
    # Display distribution
    print(f"✅ Generated with custom distribution:")
    for mapping in result['goal_question_mapping']:
        types = mapping['question_types']
        print(f"🎯 Goal: {mapping['goal_text'][:40]}...")
        print(f"   MC: {types.get('multiple_choice', 0)}, SA: {types.get('short_answer', 0)}, "
              f"Comp: {types.get('complete', 0)}, TF: {types.get('true_false', 0)}")
    
    return result

def main():
    """Run all examples"""
    print("🚀 GOAL-BASED QUESTION GENERATION - USAGE EXAMPLES")
    print("=" * 60)
    
    # Run examples
    result1 = example_with_goals()
    result2 = example_without_goals()
    result3 = example_custom_question_counts()
    
    print("\n✅ All examples completed!")
    print("\n📋 Summary:")
    print("• Example 1: Used provided goals to generate targeted questions")
    print("• Example 2: Generated goals automatically from content analysis")
    print("• Example 3: Used custom question count distribution")
    
    print("\n🔧 Integration Tips:")
    print("• Use goal_based_questions for goal-focused generation")
    print("• Use regular questions for traditional generation")
    print("• Mix both approaches based on your needs")
    print("• Check the _goal_based_metadata for generation statistics")

if __name__ == "__main__":
    main()
