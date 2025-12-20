import torch

print("Torch version:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())

if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))
    x = torch.randn(2000, 2000, device="cuda")
    y = torch.matmul(x, x)
    print("GPU computation successful")
else:
    print("Running on CPU")
