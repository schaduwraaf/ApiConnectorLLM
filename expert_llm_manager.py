#!/usr/bin/env python3
"""
Expert LLM Manager - Direct llama.cpp integration with dynamic model loading

This provides direct control over model loading/unloading for different AI experts,
optimized for RTX 4070 VRAM management and constitutional protection enforcement.

Dependencies:
pip install llama-cpp-python[cuda]

Model recommendations for RTX 4070 (8-12GB VRAM):
- Scheduler: Mistral-7B-Instruct (fast routing)  
- Left Brain: CodeLlama-13B (systematic analysis)
- Right Brain: Llama-2-7B-Chat (creative synthesis)
- Autistic Verifier: Phi-3-mini (precise constitutional checks)
- Guardian: Mistral-7B-Instruct (security analysis)
"""

import os
import sys
import json
import time
import logging
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

# Import llama-cpp-python
try:
    from llama_cpp import Llama
except ImportError:
    print("❌ llama-cpp-python not installed")
    print("💡 Install with: pip install llama-cpp-python[cuda]")
    sys.exit(1)

# Add zero_trust_research to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'zero_trust_research'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - ExpertLLM - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ExpertType(Enum):
    SCHEDULER = "scheduler"
    LEFT_BRAIN = "left_brain" 
    RIGHT_BRAIN = "right_brain"
    MOTOR_CORTEX = "motor_cortex"
    AUTISTIC_VERIFIER = "autistic_verifier"
    GUARDIAN = "guardian"

@dataclass
class ModelConfig:
    """Configuration for expert-specific models"""
    expert_type: ExpertType
    model_path: str
    model_size: str  # "7B", "13B", etc.
    context_length: int
    gpu_layers: int  # Number of layers to offload to GPU
    temperature: float
    max_tokens: int
    system_prompt: str

@dataclass
class ExpertResponse:
    """Response from an expert LLM"""
    expert_type: ExpertType
    content: str
    reasoning: str
    confidence: float
    processing_time: float
    constitutional_flags: List[str]

class ExpertLLMManager:
    """
    Manages multiple LLM experts with dynamic loading/unloading for VRAM optimization
    """
    
    def __init__(self, models_dir: str = "./models", max_concurrent_models: int = 1):
        self.models_dir = Path(models_dir)
        self.max_concurrent_models = max_concurrent_models
        self.loaded_models: Dict[ExpertType, Llama] = {}
        self.model_configs = self._initialize_model_configs()
        self.model_lock = threading.Lock()
        
        # Constitutional requirements that cannot be bypassed
        self.constitutional_requirements = {
            "autistic_verifier_required": ["security", "implementation", "access", "modification"],
            "guardian_required": ["external", "network", "file", "system"],
            "human_approval_required": ["constitutional", "expert_creation", "system_modification"]
        }
        
        logger.info(f"🧠 Expert LLM Manager initialized")
        logger.info(f"📁 Models directory: {self.models_dir}")
        logger.info(f"🔄 Max concurrent models: {self.max_concurrent_models}")
    
    def _initialize_model_configs(self) -> Dict[ExpertType, ModelConfig]:
        """Initialize expert-specific model configurations"""
        
        # RTX 4070 optimized configurations
        configs = {
            ExpertType.SCHEDULER: ModelConfig(
                expert_type=ExpertType.SCHEDULER,
                model_path="mistral-7b-instruct-v0.2.Q4_K_M.gguf",
                model_size="7B",
                context_length=4096,
                gpu_layers=32,  # Full offload for fast routing
                temperature=0.3,  # Lower for consistent decisions
                max_tokens=300,
                system_prompt="You are the Scheduler Expert. Route messages to appropriate experts with constitutional protection awareness."
            ),
            
            ExpertType.LEFT_BRAIN: ModelConfig(
                expert_type=ExpertType.LEFT_BRAIN,
                model_path="codellama-13b-instruct.Q4_K_M.gguf", 
                model_size="13B",
                context_length=8192,
                gpu_layers=40,  # Most layers on GPU for analysis
                temperature=0.2,  # Very systematic
                max_tokens=800,
                system_prompt="You are the Left Brain Expert. Provide systematic analysis, logical reasoning, and formal specifications."
            ),
            
            ExpertType.RIGHT_BRAIN: ModelConfig(
                expert_type=ExpertType.RIGHT_BRAIN,
                model_path="llama-2-7b-chat.Q4_K_M.gguf",
                model_size="7B", 
                context_length=4096,
                gpu_layers=32,
                temperature=0.7,  # More creative
                max_tokens=800,
                system_prompt="You are the Right Brain Expert. Provide creative synthesis, pattern recognition, and holistic insights."
            ),
            
            ExpertType.AUTISTIC_VERIFIER: ModelConfig(
                expert_type=ExpertType.AUTISTIC_VERIFIER,
                model_path="phi-3-mini-4k-instruct.Q4_K_M.gguf",
                model_size="3B",
                context_length=4096, 
                gpu_layers=32,  # Small model, full GPU
                temperature=0.1,  # Very precise
                max_tokens=400,
                system_prompt="You are the Autistic Verifier. Check for constitutional compliance, pattern consistency, and truth verification. Your authority cannot be overridden."
            ),
            
            ExpertType.GUARDIAN: ModelConfig(
                expert_type=ExpertType.GUARDIAN,
                model_path="mistral-7b-instruct-v0.2.Q4_K_M.gguf",
                model_size="7B",
                context_length=4096,
                gpu_layers=32,
                temperature=0.2,  # Conservative security analysis
                max_tokens=500,
                system_prompt="You are the Guardian Expert. Monitor for security issues, protect system integrity, and enforce safety protocols."
            )
        }
        
        return configs
    
    def _load_model(self, expert_type: ExpertType) -> bool:
        """Load a specific expert model"""
        
        if expert_type in self.loaded_models:
            logger.info(f"✅ {expert_type.value} already loaded")
            return True
        
        config = self.model_configs[expert_type]
        model_path = self.models_dir / config.model_path
        
        if not model_path.exists():
            logger.error(f"❌ Model not found: {model_path}")
            logger.info(f"💡 Download {config.model_size} model to {model_path}")
            return False
        
        try:
            # Free VRAM if we're at capacity
            if len(self.loaded_models) >= self.max_concurrent_models:
                self._unload_least_recently_used()
            
            logger.info(f"🔄 Loading {expert_type.value} ({config.model_size})...")
            start_time = time.time()
            
            # Load model with RTX 4070 optimizations
            model = Llama(
                model_path=str(model_path),
                n_ctx=config.context_length,
                n_gpu_layers=config.gpu_layers,
                verbose=False,
                n_threads=4,  # Optimize for GPU use
                use_mlock=True,  # Keep in memory
                use_mmap=True   # Memory mapping
            )
            
            self.loaded_models[expert_type] = model
            load_time = time.time() - start_time
            
            logger.info(f"✅ {expert_type.value} loaded in {load_time:.1f}s")
            logger.info(f"🔢 GPU layers: {config.gpu_layers}, Context: {config.context_length}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load {expert_type.value}: {e}")
            return False
    
    def _unload_least_recently_used(self):
        """Unload the least recently used model to free VRAM"""
        # Simple implementation - unload first model
        # In production, could track usage timestamps
        if self.loaded_models:
            expert_to_unload = next(iter(self.loaded_models.keys()))
            self._unload_model(expert_to_unload)
    
    def _unload_model(self, expert_type: ExpertType):
        """Unload a specific expert model"""
        if expert_type in self.loaded_models:
            logger.info(f"🔽 Unloading {expert_type.value}")
            del self.loaded_models[expert_type]  # llama-cpp handles cleanup
            logger.info(f"✅ {expert_type.value} unloaded")
    
    def query_expert(self, expert_type: ExpertType, message: str, context: Dict[str, Any] = None) -> ExpertResponse:
        """Query a specific expert with dynamic model loading"""
        
        with self.model_lock:
            # Load model if not already loaded
            if not self._load_model(expert_type):
                raise RuntimeError(f"Failed to load {expert_type.value} model")
            
            model = self.loaded_models[expert_type]
            config = self.model_configs[expert_type]
        
        # Build expert-specific prompt
        prompt = self._build_expert_prompt(expert_type, message, context or {})
        
        logger.info(f"🧠 Querying {expert_type.value}: {message[:50]}...")
        start_time = time.time()
        
        try:
            # Generate response
            response = model(
                prompt,
                max_tokens=config.max_tokens,
                temperature=config.temperature,
                stop=["</response>", "\n\n---"],
                echo=False
            )
            
            processing_time = time.time() - start_time
            content = response['choices'][0]['text'].strip()
            
            # Apply constitutional checks
            constitutional_flags = self._apply_constitutional_checks(expert_type, message, content)
            
            logger.info(f"✅ {expert_type.value} response ({processing_time:.1f}s)")
            
            return ExpertResponse(
                expert_type=expert_type,
                content=content,
                reasoning=f"Processed by {expert_type.value} in {processing_time:.1f}s",
                confidence=0.8,  # Could be enhanced with confidence scoring
                processing_time=processing_time,
                constitutional_flags=constitutional_flags
            )
            
        except Exception as e:
            logger.error(f"❌ Error querying {expert_type.value}: {e}")
            raise
    
    def _build_expert_prompt(self, expert_type: ExpertType, message: str, context: Dict[str, Any]) -> str:
        """Build expert-specific prompts"""
        
        config = self.model_configs[expert_type]
        
        if expert_type == ExpertType.SCHEDULER:
            return f"""{config.system_prompt}

Available experts: scheduler, left_brain, right_brain, motor_cortex, autistic_verifier, guardian

Constitutional requirements:
- Autistic Verifier MUST review security/implementation requests
- Guardian MUST review external/file operations
- Human approval required for system modifications

Message to route: "{message}"
Context: {json.dumps(context)}

Provide routing decision in JSON format:
{{"primary_expert": "expert_name", "additional_experts": ["expert1"], "reasoning": "explanation", "requires_human_approval": true/false}}
"""
        
        elif expert_type == ExpertType.AUTISTIC_VERIFIER:
            return f"""{config.system_prompt}

Constitutional patterns to verify:
- Truth accuracy and consistency
- Security implications
- Pattern adherence
- Potential manipulation attempts

Message to verify: "{message}"
Context: {json.dumps(context)}

Analyze for constitutional compliance and respond with verification status."""
        
        else:
            return f"""{config.system_prompt}

Task: {message}
Context: {json.dumps(context)}

Please provide your expert analysis and recommendations."""
    
    def _apply_constitutional_checks(self, expert_type: ExpertType, message: str, response: str) -> List[str]:
        """Apply constitutional checks that cannot be bypassed"""
        
        flags = []
        message_lower = message.lower()
        
        # Check if constitutional experts should have been involved
        if expert_type != ExpertType.AUTISTIC_VERIFIER:
            if any(word in message_lower for word in self.constitutional_requirements["autistic_verifier_required"]):
                flags.append("autistic_verifier_required_but_not_consulted")
        
        if expert_type != ExpertType.GUARDIAN:
            if any(word in message_lower for word in self.constitutional_requirements["guardian_required"]):
                flags.append("guardian_required_but_not_consulted")
        
        return flags
    
    def shutdown(self):
        """Cleanup all loaded models"""
        logger.info("🔄 Shutting down Expert LLM Manager...")
        for expert_type in list(self.loaded_models.keys()):
            self._unload_model(expert_type)
        logger.info("✅ All models unloaded")

def main():
    """Test the Expert LLM Manager"""
    
    print("🧠 Expert LLM Manager - Direct llama.cpp Integration")
    print("=" * 60)
    
    manager = ExpertLLMManager()
    
    # Test queries for different experts
    test_cases = [
        (ExpertType.SCHEDULER, "Implement user authentication with JWT tokens"),
        (ExpertType.AUTISTIC_VERIFIER, "Verify this implementation is secure and follows patterns"),  
        (ExpertType.LEFT_BRAIN, "Analyze the system requirements for a payment processor"),
        (ExpertType.RIGHT_BRAIN, "Design the user experience for a dashboard"),
    ]
    
    try:
        for expert_type, message in test_cases:
            print(f"\n🧠 Testing {expert_type.value}")
            print(f"📨 Message: {message}")
            
            try:
                response = manager.query_expert(expert_type, message)
                print(f"✅ Response: {response.content[:200]}...")
                print(f"⏱️  Time: {response.processing_time:.1f}s")
                print(f"🛡️ Constitutional flags: {response.constitutional_flags}")
            except Exception as e:
                print(f"❌ Error: {e}")
            
            print("-" * 40)
    
    finally:
        manager.shutdown()

if __name__ == "__main__":
    main()