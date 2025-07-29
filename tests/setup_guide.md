# Ash Crisis Detection Testing Environment Setup

Quick setup guide for testing toxic-bert and other models for the Ash project.

## Server Specifications
- **OS:** Debian 12 Linux Server
- **GPU:** RTX 3060 (12GB VRAM)
- **RAM:** 64GB
- **CPU:** Ryzen 7 5800X

## Prerequisites

- **Python 3.9-3.11** installed on Debian 12
- **NVIDIA drivers** and **CUDA** (for GPU acceleration)
- **Git** for cloning repositories (optional)
- **SSH access** to the server

## Quick Setup (Automated)

1. **SSH into your Debian server:**
   ```bash
   ssh user@10.20.30.253
   ```

2. **Download the files to your server:**
   ```bash
   # Create testing directory
   mkdir -p ~/ash-testing
   cd ~/ash-testing
   
   # Download files (or use scp/rsync from your development machine)
   # requirements.txt, setup_test_environment.sh, test_toxic_bert.py
   ```

3. **Make setup script executable and run:**
   ```bash
   chmod +x setup_test_environment.sh
   ./setup_test_environment.sh
   ```

4. **The script will automatically:**
   - Check Python, NVIDIA drivers, and CUDA
   - Create virtual environment `ash-test-env`
   - Install PyTorch with CUDA support for RTX 3060
   - Install all other dependencies
   - Test GPU acceleration
   - Show system resource information

## Manual Setup

If you prefer to set up manually:

### Step 1: Check System Requirements
```bash
# Check Python version
python3 --version

# Check NVIDIA drivers
nvidia-smi

# Check CUDA (optional but recommended for speed)
nvcc --version

# Check system resources
free -h
nproc
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv ash-test-env

# Activate it
source ash-test-env/bin/activate

# Upgrade pip
python -m pip install --upgrade pip
```

### Step 3: Install PyTorch with CUDA Support
```bash
# For RTX 3060 with CUDA 11.8 (recommended)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Verify GPU acceleration works
python -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"
```

### Step 4: Install Other Dependencies
```bash
# Install from requirements file
pip install -r requirements.txt
```

## Using the Environment

### Activate Environment
```bash
source ash-test-env/bin/activate
```

### Run Tests
```bash
# Run toxic-bert comparison test (will use GPU automatically)
python test_toxic_bert.py

# Test against your NLP server
curl -X POST http://10.20.30.253:8881/analyze \
  -H "Content-Type: application/json" \
  -d '{"message": "test phrase", "user_id": "test"}'

# Monitor GPU usage during testing
watch -n 1 nvidia-smi
```

### Deactivate Environment
```bash
deactivate
```

## Performance Optimization

### GPU Memory Management
```bash
# Check GPU memory usage
nvidia-smi

# For large models, you might want to enable memory optimization
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128
```

### Batch Processing
The RTX 3060 with 12GB VRAM can handle larger batch sizes:
```python
# In your test scripts, you can increase batch size for faster processing
BATCH_SIZE = 16  # Increase from default 8
```

## Troubleshooting

### Common Issues

**Python not found:**
```bash
# Install Python on Debian 12
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

**NVIDIA drivers not found:**
```bash
# Install NVIDIA drivers
sudo apt update
sudo apt install nvidia-driver firmware-misc-nonfree

# Reboot after installation
sudo reboot
```

**CUDA not available:**
```bash
# Install CUDA toolkit (optional but recommended)
wget https://developer.download.nvidia.com/compute/cuda/repos/debian12/x86_64/cuda-keyring_1.0-1_all.deb
sudo dpkg -i cuda-keyring_1.0-1_all.deb
sudo apt-get update
sudo apt-get -y install cuda

# Add to PATH (add to ~/.bashrc)
export PATH=/usr/local/cuda/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
```

**pip install fails:**
```bash
# Update pip and try again
python -m pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt

# If still failing, install system dependencies
sudo apt install build-essential python3-dev
```

**Out of GPU memory:**
```bash
# Monitor GPU usage
nvidia-smi

# Clear GPU cache if needed
python -c "import torch; torch.cuda.empty_cache()"
```

### GPU Performance Verification

```bash
# Test GPU acceleration
python -c "
import torch
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'GPU: {torch.cuda.get_device_name(0)}')
    print(f'Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB')
    # Quick tensor operation test
    x = torch.randn(1000, 1000).cuda()
    y = torch.mm(x, x)
    print('✅ GPU tensor operations working')
"
```

### Performance Monitoring

```bash
# Monitor during testing
htop          # CPU and RAM usage
nvidia-smi -l 1  # GPU usage every second
iotop         # Disk I/O (if available)
```

## Next Steps

1. **Test toxic-bert** on your failing phrases
2. **Compare results** with current system
3. **Decide on implementation** based on test results
4. **Integrate into ash-nlp** if results are promising

## File Structure

```
~/ash-testing/
├── ash-test-env/              # Virtual environment (created by setup)
├── requirements.txt           # Dependencies with CUDA support
├── setup_test_environment.sh  # Automated setup for Linux
├── test_toxic_bert.py        # Testing script
├── SETUP_GUIDE.md            # This file
└── results/                  # Test results (created during testing)
```

## Performance Notes

**Expected Performance with RTX 3060:**
- **Model Loading:** ~5-10 seconds
- **Inference Speed:** ~50-100ms per phrase
- **Memory Usage:** ~2-4GB GPU memory for toxic-bert
- **Batch Processing:** Can handle 16-32 phrases simultaneously

**Optimization Tips:**
- Use GPU acceleration for ~10x speedup vs CPU
- Enable mixed precision for faster inference
- Monitor GPU memory to avoid out-of-memory errors
- Use batch processing for multiple phrases

## Support

If you run into issues:
1. Check the troubleshooting section above
2. Make sure all files are in the same directory
3. Try the manual setup steps
4. Verify Python version compatibility