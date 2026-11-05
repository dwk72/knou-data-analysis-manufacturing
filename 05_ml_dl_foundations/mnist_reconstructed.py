"""Reconstruction of the submitted KNOU PyTorch MNIST exercise (code screenshots).

The network, loss, optimizer, LR and batch sizes follow the submitted PDF.
The notebook's complete source and training environment are unavailable,
so the reported historic 97.82% accuracy is NOT verified here.

Offline check: python mnist_reconstructed.py --smoke-test
Training: python mnist_reconstructed.py --download --epochs 10
"""

from __future__ import annotations

import argparse
from pathlib import Path

import torch
from torch import nn
from torch import optim


class Net(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.fc1 = nn.Linear(28 * 28, 512)
        self.fc2 = nn.Linear(512, 256)
        self.fc3 = nn.Linear(256, 10)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x.view(-1, 28 * 28)
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)


def smoke_test() -> None:
    torch.manual_seed(42)
    model = Net()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.CrossEntropyLoss()
    data = torch.rand(8, 1, 28, 28)
    target = torch.randint(0, 10, (8,))
    logits = model(data)
    assert logits.shape == (8, 10)
    loss = criterion(logits, target)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    assert torch.isfinite(loss).item()
    print(f"PASS: output shape={tuple(logits.shape)}, finite training loss")


def train(data_dir: Path, epochs: int, download: bool) -> None:
    # Imported here so the offline smoke test only requires PyTorch.
    from torchvision import datasets, transforms

    torch.manual_seed(42)
    transform = transforms.ToTensor()
    train_data = datasets.MNIST(root=data_dir, train=True, transform=transform, download=download)
    test_data = datasets.MNIST(root=data_dir, train=False, transform=transform, download=download)
    train_loader = torch.utils.data.DataLoader(train_data, batch_size=64, shuffle=True)
    test_loader = torch.utils.data.DataLoader(test_data, batch_size=1000, shuffle=False)

    model = Net()
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    for epoch in range(1, epochs + 1):
        model.train()
        sum_loss = 0.0
        samples = 0
        for data, target in train_loader:
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
            sum_loss += loss.item() * data.size(0)
            samples += data.size(0)
        print(f"Epoch {epoch}: train loss={sum_loss / samples:.6f}")

    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for data, target in test_loader:
            predicted = model(data).argmax(dim=1)
            total += target.size(0)
            correct += (predicted == target).sum().item()
    print(f"Test accuracy: {correct / total:.2%} (new run, not historic result)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke-test", action="store_true", help="Validate model and one update offline")
    parser.add_argument("--download", action="store_true", help="Allow torchvision to download MNIST")
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).resolve().parent / "data")
    args = parser.parse_args()
    if args.smoke_test:
        smoke_test()
    else:
        if args.epochs < 1:
            parser.error("--epochs must be >= 1")
        train(args.data_dir, args.epochs, args.download)


if __name__ == "__main__":
    main()
