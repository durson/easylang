# coding: utf-8

from transformers import OpenAIGPTLMHeadModel, BertTokenizer
from itertools import chain
import re
import numpy as np
import torch
import torch.nn.functional as F

from .common import *


class StateEntry:
    def __init__(self):
        self.history = []


class ZhCmnEngineLm:
    def __init__(self, cfg, engine_dict):
        seed = 1234
        torch.random.manual_seed(seed)
        torch.cuda.manual_seed(seed)

        model_checkpoint = cfg[iso()]["engine_lm"]["model_checkpoint"]
        tokenizer = BertTokenizer.from_pretrained(model_checkpoint, do_lower_case=True)
        model = OpenAIGPTLMHeadModel.from_pretrained(model_checkpoint)
        device = "cuda"
        special_tokens = ["[CLS]", "[SEP]", "[PAD]", "[speaker1]", "[speaker2]"]
        model.to(device)
        model.eval()

        count_np = np.empty([len(tokenizer)])
        for char in tokenizer.vocab:
            i = tokenizer.vocab[char]
            if char in special_tokens:
                count_np[i] = 0.0
            else:
                count_np[i] = engine_dict.get_count(char)
        count_tensor = torch.tensor(count_np, dtype=torch.float, device=device)

        self.tokenizer = tokenizer
        self.model = model
        self.device = device
        self.state = {}
        self.special_tokens = special_tokens
        self.temperature = cfg[iso()]["engine_lm"]["temperature"]
        self.top_p = cfg[iso()]["engine_lm"]["top_p"]
        self.count_tensor = count_tensor

        test = [
            "你好",
            "好呀",
            "你好吗？",
            "很好很好",
            "很高兴听你这样说",
            "没有没有",
            "问我一件事",
            "...呵呵元芳你怎么看？",
        ]

        test_i = 0
        while test_i+1 < len(test):
            prd = self.predict(100, test[test_i])
            tgt = test[test_i+1]
            if prd != tgt:
                print(f"{prd} != {tgt}")
            test_i += 2


    def tokenize(self, text):
        return self.tokenizer.convert_tokens_to_ids(self.tokenizer.tokenize(text))


    def build_input(self, history, reply):
        """ Build a sequence of input from 3 segments: persona, history and last reply """
        bos, eos, pad, speaker1, speaker2 = self.tokenizer.convert_tokens_to_ids(self.special_tokens)
        sequence = [[bos]] + history + [reply]
        sequence = [sequence[0]] + [[speaker2 if i % 2 else speaker1] + s for i, s in enumerate(sequence[1:])]
        instance = {}
        instance["input_ids"] = list(chain(*sequence))
        instance["token_type_ids"] = [bos] + [speaker2 if i % 2 else speaker1 for i, s in enumerate(sequence[1:])
                                              for _ in s]
        return instance, sequence


    def top_filtering(self, logits, top_p=0.0, threshold=-float('Inf'), filter_value=-float('Inf')):
        assert logits.dim() == 1  # Only work for batch size 1 for now - could update but it would obfuscate a bit the code
        if top_p > 0.0:
            # Compute cumulative probabilities of sorted tokens
            sorted_logits, sorted_indices = torch.sort(logits, descending=True)
            cumulative_probabilities = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)

            # Remove tokens with cumulative probability above the threshold
            sorted_indices_to_remove = cumulative_probabilities > top_p
            # Shift the indices to the right to keep also the first token above the threshold
            sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
            sorted_indices_to_remove[..., 0] = 0

            # Back to unsorted indices and set them to -infinity
            indices_to_remove = sorted_indices[sorted_indices_to_remove]
            logits[indices_to_remove] = filter_value

        indices_to_remove = logits < threshold
        logits[indices_to_remove] = filter_value
        return logits


    def vocab_filtering(self, logits, threshold, filter_value=-float('Inf')):
        assert logits.dim() == 1  # Only work for batch size 1 for now - could update but it would obfuscate a bit the code
        filter_tensor = filter_value * torch.ones_like(logits, dtype=torch.float)
        return torch.where(self.count_tensor >= threshold, logits, filter_tensor)


    def sample(self, state):
        with torch.no_grad():
            special_tokens_ids = self.tokenizer.convert_tokens_to_ids(self.special_tokens)
            out_ids = []

            min_len = 1
            max_len = 16
            for i in range(max_len):
                instance, sequence = self.build_input(state.history, out_ids)
                input_ids = torch.tensor(instance["input_ids"], dtype=torch.long, device=self.device).unsqueeze(0)
                token_type_ids = torch.tensor(instance["token_type_ids"], dtype=torch.long, device=self.device).unsqueeze(0)

                logits, *_ = self.model(input_ids, token_type_ids=token_type_ids)
                logits = logits[0, -1, :] / self.temperature
                logits = self.vocab_filtering(logits, -8.0)
                logits = self.top_filtering(logits, self.top_p)
                probs = F.softmax(logits, dim=-1)

                prev = torch.multinomial(probs, 1)
                if i < min_len and prev.item() in special_tokens_ids:
                    while prev.item() in special_tokens_ids:
                        prev = torch.multinomial(probs, num_samples=1)

                if prev.item() in special_tokens_ids:
                    break
                out_ids.append(prev.item())

        state.history.append(out_ids)
        out_text = self.tokenizer.decode(out_ids, skip_special_tokens=True)
        out_text = re.sub(r" +", "", out_text)
        return out_text


    def predict(self, corrid, text):
        state = self.state.get(corrid, None)
        if state is None:
            self.state[corrid] = StateEntry()
            state = self.state.get(corrid, None)

        state.history.append(self.tokenize(text))
        out_text = self.sample(state)
        return out_text
