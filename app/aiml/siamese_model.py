import torch
import torch.nn as nn

class SiameseNetwork(nn.Module):
    def __init__(self, embedding_dim=384):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(embedding_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 128)
        )

    def forward(self, x1, x2):
        out1 = self.fc(x1)
        out2 = self.fc(x2)
        return torch.cosine_similarity(out1, out2)
