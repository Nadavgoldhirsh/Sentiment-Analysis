import torch
import torch.nn as nn
import torch.nn.functional as F

class MySelfAttention(nn.Module):
    """
    Self attention layer
    """
    def __init__(self, input_dim):
        """
        :param input_dim: The feature dimension the input tokens (d).
        """
        super(MySelfAttention, self).__init__()
        self.input_dim = input_dim
        ### YOUR CODE HERE ###
        self.WQ = nn.Linear(input_dim, input_dim)
        self.WK = nn.Linear(input_dim, input_dim)
        self.WV = nn.Linear(input_dim, input_dim)

    def forward(self, x):
        ### YOUR CODE HERE ###

        Q = self.WQ(x)
        K = self.WK(x)
        V = self.WV(x)

        attention_scores = torch.matmul(Q, K.transpose(-1, -2)) / torch.sqrt(
            torch.tensor(self.input_dim, dtype=torch.float32))

        # Apply softmax
        attention_weights = F.softmax(attention_scores, dim=-1)

        # Weighted sum of the values (V) using the attention weights
        attended_values = torch.matmul(attention_weights, V)

        return attended_values
class MyLayerNorm(nn.Module):
    """
    Layer Normalization layer.
    """
    def __init__(self, input_dim):
        """
        :param input_dim: The dimension of the input (T, d).
        """
        super(MyLayerNorm, self).__init__()
        self.gamma = nn.Parameter(torch.ones(*input_dim))
        self.beta = nn.Parameter(torch.zeros(*input_dim))


    def forward(self, x):
        epsilon = 1e-8
        N, T, d = x.size()
        x_reshaped = x.view(N, -1)

        # Calculate mean and variance along the last dimension (T*d) for each example in the batch
        mean = torch.mean(x_reshaped, dim=1, keepdim=True)
        variance = torch.var(x_reshaped, dim=1, unbiased=False, keepdim=True)

        # Normalize the input tensor for each example in the batch
        normalized_tensor = (x_reshaped - mean) / torch.sqrt(
            variance + epsilon)  # Add small epsilon for numerical stability

        # Reshape the normalized tensor back to the original shape (N, T, d)
        normalized_tensor = normalized_tensor.view(N, T, d)

        # Scale and shift the normalized tensor using gamma and beta parameters
        scaled_tensor = self.gamma * normalized_tensor + self.beta

        return scaled_tensor









class MyTransformerBlock(nn.Module):
    """
    Transformer block.
    """
    def __init__(self, max_len, input_dim):
        super(MyTransformerBlock, self).__init__()
        self.attention = MySelfAttention(input_dim)
        self.norm1 = MyLayerNorm((max_len, input_dim))
        self.norm2 = MyLayerNorm((max_len, input_dim))
        self.fc1 = nn.Linear(input_dim, input_dim)
        self.fc2 = nn.Linear(input_dim, input_dim)
        self.dropout = nn.Dropout(0.1)

    def forward(self, x):
        out = self.attention(x)
        x = self.norm1(self.dropout(out) + x)
        out = self.fc2(F.relu(self.fc1(x)))
        out = self.norm2(out + x)
        return out

class MyTransformer(nn.Module):
    """
    Transformer.
    """
    def __init__(self, vocab, max_len, num_of_blocks):
        """
        :param vocab: The vocabulary object.
        :param num_of_blocks: The number of transformer blocks.
        """
        super(MyTransformer, self).__init__()
        self.embedding = nn.Embedding.from_pretrained(vocab.vectors)
        self.emb_dim = self.embedding.embedding_dim
        self.max_len = max_len
        self.blocks = nn.ModuleList([MyTransformerBlock(self.max_len, self.emb_dim) for _ in range(num_of_blocks)])
        self.fc = nn.Linear(self.emb_dim, 1)

    def forward(self, x):
        x = self.embedding(x)
        for block in self.blocks:
            x = block(x)
        avg_pooling = x.mean(dim=1)
        x = self.fc(avg_pooling)
        return x

