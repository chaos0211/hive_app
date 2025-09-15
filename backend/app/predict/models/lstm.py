# backend/app/predict/models/lstm.py
import torch
import torch.nn as nn

class RankLSTM(nn.Module):
    def __init__(self, in_dim: int, hidden: int = 64, layers: int = 2, horizon: int = 7, dropout: float = 0.1):
        super().__init__()
        self.lstm = nn.LSTM(input_size=in_dim, hidden_size=hidden, num_layers=layers,
                            batch_first=True, dropout=dropout if layers > 1 else 0.0)
        self.head = nn.Linear(hidden, horizon)

    def forward(self, x):  # x: [B, T, in_dim]
        y, _ = self.lstm(x)
        last = y[:, -1, :]         # 取最后时间步
        out = self.head(last)      # [B, horizon]
        return out