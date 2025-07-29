#!/bin/bash
# Setup script for Ash Crisis Detection Testing Environment
# Debian 12 Linux Server with RTX 3060, 64GB RAM, Ryzen 7 5800X

set -e  # Exit on any error

echo "========================================"
echo "🔧 Ash Crisis Detection Test Setup"
echo "🖥️  Debian 12 + RTX 3060 + 64GB RAM"
echo "========================================"
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

print_info() {
    echo -e "${BLUE}🔍${NC} $1"
}

# Check if running as root (not recommended for this setup)
if [[ $EUID -eq 0 ]]; then
    print_warning "Running as root. Consider using a non-root user for development."
fi

# Check Python version
if ! command -v python3 &> /dev/null; then
    print_error "Python3 is not installed"
    echo "Install with: sudo apt update && sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | grep -Po '(?<=Python )\d+\.\d+')
print_info "Python version: $PYTHON_VERSION"

# Check if Python version is compatible (3.9-3.11)
if ! python3 -c "import sys; exit(0 if sys.version_info >= (3,9) and sys.version_info < (3,12) else 1)" 2>/dev/null; then
    print_warning "Python version should be 3.9-3.11 for best compatibility"
fi

# Check NVIDIA GPU
print_info "Checking NVIDIA GPU..."
if command -v nvidia-smi &> /dev/null; then
    print_status "NVIDIA drivers found:"
    nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader,nounits
    echo
else
    print_warning "nvidia-smi not found. GPU acceleration may not be available."
    echo "Install NVIDIA drivers if you want GPU acceleration."
fi

# Check CUDA
if command -v nvcc &> /dev/null; then
    CUDA_VERSION=$(nvcc --version | grep -o 'release [0-9]\+\.[0-9]\+' | grep -o '[0-9]\+\.[0-9]\+')
    print_status "CUDA version: $CUDA_VERSION"
else
    print_warning "CUDA not found. Installing CPU-only PyTorch."
fi

# Check if we're in the right directory
if [[ ! -f "requirements.txt" ]]; then
    print_error "requirements.txt not found in current directory"
    echo "Please make sure you're in the ash project directory"
    exit 1
fi

# Create virtual environment
ENV_NAME="ash-test-env"
print_info "Creating virtual environment '$ENV_NAME'..."
python3 -m venv $ENV_NAME

# Activate virtual environment
print_info "Activating virtual environment..."
source $ENV_NAME/bin/activate

# Upgrade pip
print_info "Upgrading pip..."
python -m pip install --upgrade pip

# Install PyTorch with CUDA support if available
if command -v nvcc &> /dev/null; then
    print_info "Installing PyTorch with CUDA support..."
    # Install PyTorch with CUDA 11.8 (most compatible with RTX 3060)
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
else
    print_info "Installing PyTorch CPU-only version..."
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
fi

# Install other requirements
print_info "Installing remaining dependencies..."
echo "This may take a few minutes..."
pip install -r requirements.txt

echo
echo "========================================"
echo "🧪 Testing Installation"
echo "========================================"

# Test core dependencies
print_info "Testing core dependencies..."

# Test PyTorch and CUDA
python3 << EOF
import torch
print(f"✅ PyTorch: {torch.__version__}")
print(f"✅ CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"✅ CUDA device: {torch.cuda.get_device_name(0)}")
    print(f"✅ CUDA memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB")
EOF

# Test other dependencies
python3 -c "import transformers; print(f'✅ Transformers: {transformers.__version__}')"
python3 -c "import numpy; print(f'✅ NumPy: {numpy.__version__}')"
python3 -c "import scipy; print(f'✅ SciPy: {scipy.__version__}')"
python3 -c "import requests; print(f'✅ Requests: {requests.__version__}')"

# Test GPU memory and system resources
echo
print_info "System resources:"
python3 << EOF
import psutil
print(f"✅ CPU cores: {psutil.cpu_count()}")
print(f"✅ RAM total: {psutil.virtual_memory().total / 1024**3:.1f}GB")
print(f"✅ RAM available: {psutil.virtual_memory().available / 1024**3:.1f}GB")
EOF

echo
echo "========================================"
echo "✅ Setup Complete!"
echo "========================================"
echo
echo "📝 To use the environment:"
echo "   1. Activate: source $ENV_NAME/bin/activate"
echo "   2. Run tests: python test_toxic_bert.py"
echo "   3. Deactivate: deactivate"
echo
echo "🔧 Environment location: $(pwd)/$ENV_NAME"
echo "🖥️  GPU acceleration: $(python3 -c 'import torch; print("Enabled" if torch.cuda.is_available() else "Disabled")')"
echo

# Make the toxic-bert test script executable
if [[ -f "test_toxic_bert.py" ]]; then
    chmod +x test_toxic_bert.py
    print_status "Made test_toxic_bert.py executable"
fi

print_info "Ready to test! Run: python test_toxic_bert.py"