# Copyright (c) Microsoft Corporation. 
# Licensed under the MIT license.
import torch
import torch.nn as nn
import torch
from torch.autograd import Variable
import copy
import torch.nn.functional as F
from torch.nn import CrossEntropyLoss, MSELoss

class RobertaClassificationHead(nn.Module):
    """Head for sentence-level classification tasks."""

    def __init__(self, config):
        super().__init__()
        # self.dense = nn.Linear(config.hidden_size*2, config.hidden_size)  # 分开
        self.dense = nn.Linear(config.hidden_size, config.hidden_size)  # 合并
        self.dense.weight.data.normal_(0, 0.1)  # new add
        # self.ln = nn.LayerNorm(config.hidden_size)  # new
        l2n = int(config.hidden_size/2)
        self.dense2 = nn.Linear(config.hidden_size, l2n)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
        self.out_proj = nn.Linear(l2n, 2)

    def forward(self, features, **kwargs):
        x = features[:, 0, :]  # take <s> token (equiv. to [CLS])
        # x = x.reshape(-1,x.size(-1)*2)  # 分开
        x = self.dropout(x)
        x = self.dense(x)
        # x = self.ln(x)  # new
        x = torch.tanh(x)
        x = self.dropout(x)  #
        x = self.dense2(x)  #
        x = torch.tanh(x)  #
        x = self.dropout(x)
        x = self.out_proj(x)
        return x
        
class Model(nn.Module):   
    def __init__(self, encoder,config,tokenizer,args):
        super(Model, self).__init__()
        self.encoder = encoder
        self.config=config
        self.tokenizer=tokenizer
        self.classifier=RobertaClassificationHead(config)
        self.args=args
        self.hidden_size = config.hidden_size
        self.lstm_model.lstm_head = torch.nn.LSTM(input_size=self.hidden_size,
                                       hidden_size=self.hidden_size,
                                       num_layers=2,
                                       bidirectional=True,
                                       batch_first=True)
        self.lstm_model.mlp_head = nn.Sequential(nn.Linear(2 * self.hidden_size, self.hidden_size),
                                      nn.ReLU(),
                                      nn.Linear(self.hidden_size, self.hidden_size))
    
        
    def forward(self, input_ids=None, labels=None, token_group=None):
        # input_ids=input_ids.view(-1,self.args.block_size)  # 分开
        # todo group embedding process
        outputs = self.encoder(input_ids=input_ids, attention_mask=input_ids.ne(1),
                               token_group=token_group, lstm_model=self.lstm_model)[0]
        logits=self.classifier(outputs)
        prob=F.softmax(logits)
        if labels is not None:
            loss_fct = CrossEntropyLoss()
            loss = loss_fct(logits, labels)
            return loss,prob
        else:
            return prob
      
        
 
        


