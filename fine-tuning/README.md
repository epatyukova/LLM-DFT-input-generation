(1) The training is working, but expensive (requires at least 40GB of GPU memory and who knows how many hours), need to use peft in order not to train all weights <br>
(2) Tried to do PEFT (LORA for LLama3-8b and TinyLlama1.1B). Unsloth is indeed accelerates training substantially. Quantifying base models as well (realistically can't avoid it for our use case) <br>
(3) Useful review of small LLMs https://arxiv.org/abs/2409.15790 <br>
