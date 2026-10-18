# ML / Agent 訓練與評測：100 項研究及企業實務資源

資料整理日期：2026-10-18。範圍涵蓋機器學習切分與 MLOps、LLM/Agent 評測、提示詞／模型改善、監控、學術研究、試題心理計量。每項為一個獨立文件、論文或公開課程／工具資源；共 **100** 項，連結去重 **100** 項。

## 取用深度與限制

這是依當次網路檢索結果整理的**可追溯研究資源索引**。優先資料的摘要或官方內容已用於下方結論；**不表示已逐字讀完100份全文、複現其實驗或證實每份研究品質相同**。有些論文以摘要為主，開源工具與官方文檔則核對產品描述。使用前應再檢查版本與服務可用性。此表是「可查閱資源」而不是訓練資料，也不代表已訓練模型。

## 應用結論（對本 Agent）

1. 先定義任務與可稽核成果，再做基準測試；每次修改需保留版本、trace 與回歸結果。
2. 企業 Agent 評測宜分為終局任務成功率、工具與來源正確性、生成試題品質、安全與成本；不可混成一個90%準確率。
3. 發展資料可反覆迭代，真正盲測資料在正式候選版凍結後才開封；公開歷屆題已被前一版使用，不能聲稱從未洩漏。
4. 模擬考題最重要的長期品質還包括實測難度、鑑別度、選項功能、等值性及評分者一致性；專家審稿通過率不等於完整心理計量效度。
5. 優先優化提示詞、RAG與來源驗證、資料管線、工具和測試；沒有獨立資料、成本授權與可用訓練平台，不得稱底層模型已完成訓練。
6. OpenAI 舊版 Evals/graders/prompt-optimizer 介面已公告於2026-10-31進入唯讀並於2026-11-30停止；不要將長期流程綁死在即將淘汰的產品上，應優先採獨立可攜的 pytest + 評測紀錄格式。

## 資源清單

### ML 資料切分與 MLOps

001. [Google ML Crash Course — course hub](https://developers.google.com/machine-learning/crash-course/)
002. [Google MLCC — dividing datasets](https://developers.google.com/machine-learning/crash-course/overfitting/dividing-datasets)
003. [Google MLCC — overfitting](https://developers.google.com/machine-learning/crash-course/overfitting/overfitting)
004. [Google MLCC — dataset characteristics](https://developers.google.com/machine-learning/crash-course/overfitting/data-characteristics)
005. [Google MLCC — generalization](https://developers.google.com/machine-learning/crash-course/overfitting/generalization)
006. [Google MLCC — classification metrics](https://developers.google.com/machine-learning/crash-course/classification/accuracy-precision-recall?hl=en)
007. [Google MLCC — monitoring pipelines](https://developers.google.com/machine-learning/crash-course/production-ml-systems/monitoring)
008. [Google MLCC — deployment testing](https://developers.google.com/machine-learning/crash-course/production-ml-systems/deployment-testing)
009. [Google MLCC — production questions](https://developers.google.com/machine-learning/crash-course/production-ml-systems/questions)
010. [Google Cloud — MLOps CI/CD/CT](https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning)
011. [Google Cloud — TFX MLOps architecture](https://docs.cloud.google.com/architecture/architecture-for-mlops-using-tfx-kubeflow-pipelines-and-cloud-build?hl=en)
012. [Google Cloud — ML best practices](https://docs.cloud.google.com/architecture/ml-on-gcp-best-practices)
013. [Google Cloud — ML operations architecture guides](https://docs.cloud.google.com/architecture/ai-ml/ml-application-operations-architecture-guides)

### Microsoft Agent 評測

014. [Microsoft Foundry — evaluate agents](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluate-agent)
015. [Microsoft Foundry — portal evaluations](https://learn.microsoft.com/en-us/azure/ai-studio/how-to/evaluate-generative-ai-app)
016. [Microsoft Foundry — agent evaluators](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/agent-evaluators)
017. [Microsoft Foundry — evaluation approach](https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/evaluation-approach-gen-ai)

### OpenAI 評測與模型改善

018. [OpenAI — model optimization](https://developers.openai.com/api/docs/guides/model-optimization)
019. [OpenAI — Evals API guidance (deprecated)](https://developers.openai.com/api/docs/guides/evals)
020. [OpenAI — graders (deprecated)](https://developers.openai.com/api/docs/guides/graders)
021. [OpenAI — prompt optimizer (deprecated)](https://developers.openai.com/api/docs/guides/prompt-optimizer)
022. [OpenAI — reinforcement fine-tuning (availability restricted)](https://developers.openai.com/api/docs/guides/reinforcement-fine-tuning)
023. [OpenAI — RFT use cases](https://developers.openai.com/api/docs/guides/rft-use-cases)

### Anthropic Agent 工程

024. [Anthropic — demystifying agent evals](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
025. [Anthropic — multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)
026. [Anthropic — AI-resistant technical evals](https://www.anthropic.com/engineering/AI-resistant-technical-evaluations)
027. [Anthropic — managed agents architecture](https://www.anthropic.com/engineering/managed-agents)
028. [Anthropic — long-running app harness](https://www.anthropic.com/engineering/harness-design-long-running-apps)
029. [Anthropic — effective long-running harnesses](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
030. [Anthropic — engineering article index](https://www.anthropic.com/engineering)

### LangChain / LangSmith AgentOps

031. [LangChain — agent evaluation readiness checklist](https://www.langchain.com/blog/agent-evaluation-readiness-checklist)
032. [LangChain — common agent eval questions](https://www.langchain.com/blog/common-questions-about-agent-evals)
033. [LangChain — observability powers evaluation](https://www.langchain.com/blog/agent-observability-powers-agent-evaluation)
034. [LangChain — multi-turn evals](https://www.langchain.com/blog/insights-agent-multiturn-evals-langsmith)
035. [LangChain — search agent traces](https://www.langchain.com/blog/agent-traces-ai-search-langsmith)
036. [LangChain — reusable evaluators](https://www.langchain.com/blog/reusable-langsmith-evaluator-templates)
037. [LangChain — Jev evaluator](https://www.langchain.com/blog/jev-is-now-available-in-langsmith-evals)
038. [LangChain — tuned evaluators](https://www.langchain.com/blog/introducing-langsmith-tuned-evaluators-starting-with-perceived-error)
039. [LangChain — how Deep Agents evals are built](https://www.langchain.com/blog/how-we-build-evals-for-deep-agents)
040. [LangSmith — evaluation types](https://docs.langchain.com/langsmith/evaluation-types)

### AWS AgentCore / Bedrock 評測與運維

041. [AWS — test/troubleshoot Bedrock agent](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-test.html)
042. [AWS — tutorial test Bedrock agent](https://docs.aws.amazon.com/bedrock/latest/userguide/agent-tutorial-step3.html)
043. [AWS — AgentCore evaluations](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/evaluations.html)
044. [AWS — AgentCore evaluations internals](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/how-it-works-evaluations.html)
045. [AWS — AgentCore evaluators](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/evaluators.html)
046. [AWS — evaluate Bedrock resources](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation.html)
047. [AWS — test a knowledge base](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-test.html)
048. [AWS — reliable agent evaluations](https://aws.amazon.com/blogs/machine-learning/build-reliable-ai-agents-with-amazon-bedrock-agentcore-evaluations/)
049. [AWS — AgentCore and GitHub Actions evals](https://aws.amazon.com/blogs/machine-learning/automated-agent-evaluation-with-amazon-bedrock-agentcore-and-github-actions/)
050. [AWS — custom code evaluators](https://aws.amazon.com/blogs/machine-learning/build-custom-code-based-evaluators-in-amazon-bedrock-agentcore/)
051. [AWS — AgentOps at scale](https://aws.amazon.com/blogs/machine-learning/agentops-operationalize-agentic-ai-at-scale-with-amazon-bedrock-agentcore/)
052. [AWS — Amazon Nova LLM judge](https://aws.amazon.com/blogs/machine-learning/evaluating-generative-ai-models-with-amazon-nova-llm-as-a-judge-on-amazon-sagemaker-ai/)
053. [AWS — fine tuning via LLM judge](https://aws.amazon.com/blogs/machine-learning/reinforcement-fine-tuning-with-llm-as-a-judge/)
054. [AWS — rubric-based Nova judge](https://aws.amazon.com/blogs/machine-learning/evaluate-generative-ai-models-with-an-amazon-nova-rubric-based-llm-judge-on-amazon-sagemaker-ai-part-2/)

### MLflow 評測資料與可觀測性

055. [MLflow — prompt evaluation](https://mlflow.org/docs/latest/genai/prompt-registry/evaluate-prompts/)
056. [MLflow — build evaluation datasets](https://mlflow.org/docs/latest/genai/datasets)
057. [MLflow — evaluate production traces](https://mlflow.org/docs/latest/genai/eval-monitor/running-evaluation/traces/)
058. [MLflow — prompt experiments](https://www.mlflow.org/docs/latest/genai/eval-monitor/running-evaluation/prompts/)
059. [MLflow — evaluation examples](https://mlflow.org/docs/latest/genai/eval-monitor/running-evaluation/eval-examples/)
060. [MLflow — evaluation driven workflow](https://mlflow.org/docs/latest/genai/datasets/end-to-end-workflow)
061. [MLflow — dataset concepts](https://mlflow.org/docs/latest/genai/concepts/evaluation-datasets/)
062. [MLflow — LLM/agent eval platform](https://mlflow.org/docs/latest/genai/eval-monitor/index.html)
063. [MLflow — evaluation datasets SDK](https://mlflow.org/docs/latest/genai/datasets/sdk-guide/)
064. [MLflow — classical model evaluation (distinguish from GenAI)](https://mlflow.org/docs/latest/ml/evaluation)

### 開源工具與範例

065. [UK AI Security Institute — Inspect AI repo](https://github.com/UKGovernmentBEIS/inspect_ai)
066. [UK AI Security Institute — Inspect AI docs](https://inspect.aisi.org.uk/)
067. [UK AI Security Institute — evaluation catalogue](https://inspect.aisi.org.uk/evals/)
068. [Stanford DSPy — automatic optimizers](https://github.com/stanfordnlp/dspy/blob/main/docs/docs/learn/optimization/optimizers.md)

### 研究：Agent、模型評測與資料洩漏

069. [2026 Springer — Agent eval meta-taxonomy](https://link.springer.com/article/10.1007/s10462-026-11678-4)
070. [2026 ACL — Survey on Evaluation of LLM-based Agents](https://aclanthology.org/2026.findings-acl.1330/)
071. [2025 ACM KDD — Evaluation and Benchmarking of LLM Agents](https://doi.org/10.1145/3711896.3736570)
072. [2026 Springer — From benchmarks to deployment](https://doi.org/10.1007/s10462-026-11571-0)
073. [2024 arXiv — Benchmark Data Contamination survey](https://arxiv.org/abs/2406.04244)
074. [2025 ICML — Benchmark contamination mitigation](https://proceedings.mlr.press/v267/sun25t.html)
075. [2025 ICML — Kernel divergence dataset leakage](https://proceedings.mlr.press/v267/choi25b.html)
076. [2023 ICLR — AgentBench](https://arxiv.org/abs/2308.03688)
077. [2023 arXiv — GAIA assistant benchmark](https://arxiv.org/abs/2311.12983)
078. [2023 arXiv — SWE-bench](https://arxiv.org/abs/2310.06770)
079. [2023 ICLR — ReAct](https://arxiv.org/abs/2210.03629)
080. [2023 arXiv — Self-Refine](https://arxiv.org/abs/2303.17651)
081. [2023 arXiv — MT-Bench / Chatbot Arena judge](https://arxiv.org/abs/2306.05685)
082. [2023 arXiv — G-Eval](https://arxiv.org/abs/2303.16634)
083. [2023 arXiv — Prometheus evaluation model](https://arxiv.org/abs/2310.08491)
084. [2023 arXiv — Direct Preference Optimization](https://arxiv.org/abs/2305.18290)
085. [2026 ICML — Adaptive testing via IRT](https://proceedings.mlr.press/v306/li26fx.html)
086. [2025 KDD — LLM agent evaluation tutorial materials](https://github.com/SAP-samples/llm-agents-eval-tutorial)
087. [2023 arXiv — WebArena real-world web agent benchmark](https://arxiv.org/abs/2307.13854)
088. [2024 arXiv — τ-bench multi-turn tool agent benchmark](https://arxiv.org/abs/2406.12045)

### 試題編製、醫學教育與心理計量

089. [NBME — sixth edition Item-Writing Guide](https://www.nbme.org/institutions/nbme-item-writing-guide/)
090. [2026 Oxford — validity of AI-generated medical MCQs review](https://pubmed.ncbi.nlm.nih.gov/42160214/)
091. [2026 PLOS ONE — MCQ-generation network meta-analysis](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0340277)
092. [2026 Medical Teacher — AI exams meta-analysis](https://pubmed.ncbi.nlm.nih.gov/42323886/)
093. [2025 PubMed — AI versus human MCQs in high-stakes exam](https://pubmed.ncbi.nlm.nih.gov/39923067/)
094. [2025 PubMed — case-based anatomy MCQ psychometrics](https://pubmed.ncbi.nlm.nih.gov/40129054/)
095. [2026 PubMed — pediatric education AI vs human MCQ analysis](https://pubmed.ncbi.nlm.nih.gov/41789187/)
096. [2026 PubMed — imaging-specialty MCQ psychometrics](https://pubmed.ncbi.nlm.nih.gov/41507355/)
097. [2026 BMC — randomized trial AI vs student MCQs](https://link.springer.com/article/10.1186/s12909-026-09671-0)
098. [2024 Oxford — MCQ prompts and validity review](https://doi.org/10.1093/postmj/qgae065)
099. [2026 GitHub — LLM-CAT medical adaptive testing](https://github.com/zjiang4/LLM-CAT)
100. [2026 Wiley — biomedical MCQ LLM performance meta-analysis](https://anatomypubs.onlinelibrary.wiley.com/doi/10.1002/ase.70262)

