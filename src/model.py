import os
import sys
import transformers
sys.path.append(os.getcwd())
from src import config
import torch.nn as nn

class BERTBaseUncased(nn.Module):
    def __init__(self):
        super(BERTBaseUncased, self).__init__()
        self.bert = transformers.BertModel.from_pretrained(config.BERT_PATH)
        self.bert_drop = nn.Dropout(p=0.3)
        self.out = nn.Linear(768, 1)

    def forward(self, ids, mask, token_type_ids):
        out = self.bert(
            ids, 
            attention_mask = mask, 
            token_type_ids=token_type_ids
        )
        #print("this is the output1", out.last_hidden_state)
        #print("this is the output2", out.pooler_output)
        bo = self.bert_drop(out.pooler_output)
        output = self.out(bo)
        #linear output, see dimensions of output layer above
        return output




