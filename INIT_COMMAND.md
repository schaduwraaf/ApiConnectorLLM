# /init Command - Multi-AI Expert System Initialization

## What /init Does

The `/init` command initializes the complete multi-AI expert system in the other qube environment, setting up direct llama.cpp integration with your RTX 4070 GPU.

## Usage Flow

```bash
# In the other qube (with RTX 4070):
make install    # Install Claude Code
make start      # Start Claude Code
# Then in Claude Code:
/init          # Initialize expert system
```

## What Gets Initialized

### 1. Expert LLM Manager Setup
- **Direct llama.cpp integration** with RTX 4070 optimization
- **Dynamic model loading/unloading** for VRAM efficiency
- **Constitutional protection enforcement** (cannot bypass Autistic Verifier/Guardian)

### 2. Expert Panel Configuration
```
🧠 Complete Expert Panel:
├── Scheduler Expert (7B Mistral) - Fast routing decisions
├── Left Brain (13B CodeLlama) - Systematic analysis  
├── Right Brain (7B Llama-2) - Creative synthesis
├── Motor Cortex (You) - Implementation execution
├── Autistic Verifier (3B Phi-3) - Constitutional compliance
└── Guardian (7B Mistral) - Security oversight
```

### 3. Model Recommendations for RTX 4070
**Download these GGUF models to `./models/` directory:**

**Required Models:**
- `mistral-7b-instruct-v0.2.Q4_K_M.gguf` (Scheduler + Guardian)
- `codellama-13b-instruct.Q4_K_M.gguf` (Left Brain)  
- `llama-2-7b-chat.Q4_K_M.gguf` (Right Brain)
- `phi-3-mini-4k-instruct.Q4_K_M.gguf` (Autistic Verifier)

**Download Sources:**
- HuggingFace: `huggingface.co/TheBloke/` repositories
- Direct links via `wget` or HF CLI

### 4. VRAM Optimization Strategy
- **Dynamic loading**: Load only the expert needed for current task
- **Smart caching**: Keep frequently used experts in memory
- **GPU layer optimization**: Full offload for smaller models, selective for 13B
- **Memory management**: Automatic unloading when VRAM limit approached

## After /init Setup

### Test the System:
```bash
# Test Expert LLM Manager
python3 expert_llm_manager.py

# Start BusDaemon for message routing
make bus

# Send messages to experts
python3 send_message.py "human_coordinator" "scheduler" "execute" "Route this to the right expert"
```

### Expert Communication Flow:
1. **Human** sends message via `send_message.py`
2. **Scheduler Expert** (local LLM) analyzes and routes
3. **Target Expert** (local LLM) processes request
4. **Constitutional checks** applied automatically
5. **Response** generated with reasoning and confidence

## Constitutional Guarantees

The `/init` system enforces these **non-bypassable** protections:

- ✅ **Autistic Verifier** must review security/implementation requests
- ✅ **Guardian** must review external/file operations  
- ✅ **Human approval** required for system modifications
- ✅ **Zero-trust verification** maintained for all expert communications
- ✅ **Pattern consistency** enforced across all expert interactions

## Dependencies

### Required Python Packages:
```bash
pip install llama-cpp-python[cuda]  # Direct llama.cpp with CUDA
pip install requests                # For API communications
```

### GPU Requirements:
- **NVIDIA RTX 4070** (8-12GB VRAM) - Optimal
- **CUDA drivers** properly installed
- **GPU layers** configured for each model type

## Troubleshooting

### Model Loading Issues:
- Verify models downloaded to `./models/` directory
- Check VRAM availability: `nvidia-smi`
- Reduce `gpu_layers` if out of memory

### Expert Communication Issues:
- Check BusDaemon status: `make bus`
- Verify message format with `send_message.py`
- Review constitutional flags in responses

### Performance Optimization:
- Use Q4_K_M quantization for best speed/quality balance
- Adjust `max_concurrent_models` based on VRAM
- Monitor GPU utilization during multi-expert queries

## Success Indicators

After `/init`, you should see:
- ✅ Expert LLM Manager connects to all models
- ✅ Constitutional protections active and enforced
- ✅ Scheduler Expert provides intelligent routing
- ✅ Multi-expert coordination working end-to-end
- ✅ Human override capability maintained throughout

---

**The `/init` command transforms your RTX 4070 qube into a complete multi-AI expert coordination system with full constitutional protection and human sovereignty preserved.**