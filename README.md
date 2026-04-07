# RefactoredAgent

graph TD
    %% 実行の起点
    Client[クライアント/呼び出し元] -->|インスタンス化 & run()| Pipeline[agent_/pipeline.py]
    
    %% pipeline.py が統合する要素
    Pipeline -->|グラフ構造の定義| GraphSpec[agent_/graph_spec.py]
    Pipeline -->|各処理ノードの登録| Nodes[agent_/nodes.py]
    Pipeline -->|LLMインスタンスの生成| LLM[agent_/llm/azure_llm_instance.py]
    Pipeline -->|設定の読み込み| Config[agent_/config.py]
    Pipeline -->|ログ出力| Logger[agent_/utils/logger.py]

    %% nodes.py が依存するもの
    Nodes -->|State型の参照| StateTypes[agent_/state_types.py]
    Nodes -->|外部API・LLM推論の実行| Tools[(agent_/tools/ 配下のモジュール群)]
    
    %% tools 配下の詳細 (代表例)
    Tools -.-> PCF[pcf_api.py\nPubCaseFinder]
    Tools -.-> Gestalt[gestalt_matcher.py\n画像解析]
    Tools -.-> ZeroShot[zero_shot.py\n初期推論]
    Tools -.-> Diagnosis[diagnosis.py\n統合推論]
    Tools -.-> Reflection[reflection.py\n自己評価]
    
    %% データ構造
    StateTypes -->|型定義| Models[agent_/models.py]
    Tools -->|型定義| Models

  
