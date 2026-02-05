"""Test script for SiliconFlow API integration."""

import asyncio
from langchain_core.messages import HumanMessage

from app.core.logging import logger
from app.services.llm import LLMRegistry, llm_service


async def test_siliconflow_models():
    """Test SiliconFlow models."""
    
    logger.info("starting_siliconflow_test")
    
    # Display available models
    available_models = LLMRegistry.get_all_names()
    logger.info("available_models", models=available_models, count=len(available_models))
    
    print("\n" + "="*60)
    print("Available Models:")
    for i, model in enumerate(available_models, 1):
        print(f"{i}. {model}")
    print("="*60 + "\n")
    
    # Test message
    test_messages = [
        HumanMessage(content="你好！请用一句话介绍你自己，告诉我你是什么模型。")
    ]
    
    # Test the default model (siliconflow-deepseek-v3.2)
    try:
        logger.info("testing_default_model")
        print("\n🚀 Testing default model (SiliconFlow DeepSeek V3.2)...\n")
        
        response = await llm_service.call(messages=test_messages)
        
        print("✅ Success!")
        print(f"Response: {response.content}\n")
        
        logger.info(
            "model_test_success",
            model="siliconflow-deepseek-v3.2",
            response_length=len(response.content)
        )
    except Exception as e:
        logger.exception("model_test_failed", model="siliconflow-deepseek-v3.2")
        print(f"❌ Failed: {str(e)}\n")
    
    # Test specific model by name
    if "siliconflow-deepseek-v3.2" in available_models:
        try:
            logger.info("testing_specific_model", model="siliconflow-deepseek-v3.2")
            print("🚀 Testing specific model by name...\n")
            
            response = await llm_service.call(
                messages=[HumanMessage(content="用Python写一个快速排序函数")],
                model_name="siliconflow-deepseek-v3.2"
            )
            
            print("✅ Code generation success!")
            print(f"Response:\n{response.content}\n")
            
            logger.info("code_generation_test_success")
        except Exception as e:
            logger.exception("code_generation_test_failed")
            print(f"❌ Failed: {str(e)}\n")
    
    print("="*60)
    print("✅ All tests completed!")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(test_siliconflow_models())
