<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/study-scene-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/study-scene-light.svg">
  <img src="./assets/study-scene-dark.svg" alt="an engineer's study — a desk with a retro computer, a lamp, a mechanical watch, and a rainy window with a distant city outside" width="100%"/>
</picture>

**shubham sengupta**

<sub>machine learning, built from the ground up &nbsp;·&nbsp; and then checked against the ground truth</sub>

</div>

<br>

My career was built on professional skepticism: uncovering where enterprise software quietly lies, designing resilient automated workflows, and scaling modern solutions across Swiss Re, Qualcomm, PwC, and Cognizant.
These days, I point that same suspicion at machine learning models and build them every day.

Two habits carry over. I rebuild things until I understand them: a network only felt real to me once I'd written its backprop by hand. And I measure what a system does against ground truth, not against what it says about itself. Most of what I find worth writing down comes from the gap between those two.

<div align="center">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/margin-net-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/margin-net-light.svg">
  <img src="./assets/margin-net-dark.svg" alt="a hand-sketched neural network: a signal passes forward, a gradient flows back" width="460"/>
</picture>
</div>

### on the desk, finished

**[judge-calibration](https://github.com/senguptashubham/judge-calibration)** &nbsp;<sub>· [interactive site ↗](https://senguptashubham.github.io/judge-calibration/)</sub><br>
Do LLM judges know when they're wrong? I tested three open-weight judges on 1,904 MT-Bench comparisons graded against human votes, on clean inputs and under position-swap and padding attacks. Qwen2.5-7B says it is 95% sure but is right 76% of the time. A pipeline that auto-accepts its verdicts at ≥ 0.90 confidence lets 98% of the wrong ones through. Cheap signals like order-swap agreement catch far more errors. A learned meta-model over those signals, Bayesian ones included, never significantly beat the best single signal.

**[crater-detection-yolo-vs-owlv2](https://github.com/senguptashubham/crater-detection-yolo-vs-owlv2)**<br>
A fine-tuned specialist (YOLOv8) against a zero/one-shot generalist (OWLv2) on lunar and Mars craters, all on a 6 GB laptop GPU. The specialist wins in-distribution by ~660× AP and runs ~350× faster. On a held-out set it had never seen, it loses 84% of its AP.

**[shubhamLearnsMachine](https://github.com/senguptashubham/shubhamLearnsMachine)**<br>
The foundations, rebuilt one at a time. It has an MLP in raw NumPy, a Conv2D layer via im2col checked against `nn.Conv2d`, and hand-rolled RNNs and LSTMs up to a character-level Shakespeare model. It also takes a CIFAR-10 CNN from 73.9% to 82.4% through training method alone.

### on the desk, next

Where my attention goes, roughly in the order it gets built:

- **retrieval and memory.** How a system decides what to fetch, what to keep, and what to let go of. This covers RAG done carefully and memory that forgets by disuse rather than by overwriting.
- **agents you can audit.** Tool-using systems whose failures you can find before your users do.
- **evaluation past accuracy.** Calibration, robustness, and what it actually costs to trust a model's output.
- **past next-token prediction.** Small models, world models and JEPA-style objectives, and diffusion language models.

Whatever has become real is in the pinned repos below. Ideas stay off this page until they have results.

I read philosophy for fun. The question I keep pulling on sits where the two meet: can a system trained to predict the next token ever be more than that, or is the question malformed from the start? No answers yet.

<div align="center">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/divider-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/divider-light.svg">
  <img src="./assets/divider-dark.svg" alt="" width="240"/>
</picture>
</div>

### working together

Open to collaboration and professional work, especially where these help:

- **evaluating an LLM or RAG pipeline before it ships.** That means test sets, LLM-as-judge setups that are checked for calibration and bias, and regression checks that catch silent failures.
- **fine-tuning and benchmarking models on real constraints.** Your data, your hardware budget, and an honest comparison against the off-the-shelf option.
- **test-automation discipline brought to ML code.** Pytest suites, pinned environments, and runs that reproduce.

<br>

### the shelf

<div align="center">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/bookshelf-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/bookshelf-light.svg">
  <img src="./assets/bookshelf-dark.svg" alt="two shelves of books: the tools in daily use on top — python, numpy, pytorch, transformers, vllm, ultralytics, scikit-learn, numpyro, pandas, matplotlib, jupyter — and the testing tools that came before on the bottom — selenium, java, c#, playwright, cucumber, postman, jenkins, oracle" width="100%"/>
</picture>
</div>

<br>

<div align="center">

<sub>[linkedin ↗](https://www.linkedin.com/in/senguptashubham) &nbsp;·&nbsp; [judge-calibration on hugging face ↗](https://huggingface.co/spaces/shubhamsengupta/judge-calibration)</sub>

</div>
