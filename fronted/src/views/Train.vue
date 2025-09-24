<template>
  <div class="bg-gray-50 font-inter text-dark min-h-screen">
    <div class="container mx-auto px-4 py-6 max-w-7xl">
      <!-- 训练概览区 -->
      <div class="bg-white rounded-xl shadow-card p-6 mb-6 card-transition hover:shadow-card-hover">
        <div class="flex flex-col md:flex-row md:items-center justify-between mb-6">
          <div>
            <h1 class="text-[clamp(1.5rem,3vw,2rem)] font-bold text-dark mb-2">模型训练中心</h1>
            <p class="text-dark-2">实时监控模型训练过程、评估训练结果与历史模型性能</p>
          </div>
          <div class="flex space-x-3 mt-4 md:mt-0">
            <button class="bg-primary hover:bg-primary/90 text-white px-4 py-2 rounded-lg flex items-center transition-all">
              <i class="fas fa-plus mr-2"></i> 新建训练
            </button>
            <button class="bg-white border border-light-2 hover:border-primary text-dark px-4 py-2 rounded-lg flex items-center transition-all">
              <i class="fas fa-download mr-2"></i> 导出报告
            </button>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <div class="bg-light-1 rounded-lg p-4"><p class="text-dark-2 text-sm mb-1">模型类型</p><p class="font-semibold">LSTM时序预测模型</p></div>
          <div class="bg-light-1 rounded-lg p-4"><p class="text-dark-2 text-sm mb-1">训练数据范围</p><p class="font-semibold">中国 · iOS · 免费榜 · 游戏</p></div>
          <div class="bg-light-1 rounded-lg p-4"><p class="text-dark-2 text-sm mb-1">数据拆分比例</p><p class="font-semibold">70% / 15% / 15%</p></div>
          <div class="bg-light-1 rounded-lg p-4"><p class="text-dark-2 text-sm mb-1">随机种子</p><p class="font-semibold">42</p></div>
          <div class="bg-light-1 rounded-lg p-4"><p class="text-dark-2 text-sm mb-1">运行环境</p><p class="font-semibold">GPU: Tesla V100</p></div>
          <div class="bg-light-1 rounded-lg p-4">
            <p class="text-dark-2 text-sm mb-1">训练状态</p>
            <div class="flex items-center">
              <span class="inline-block w-2 h-2 bg-success rounded-full mr-2 animate-pulse"></span>
              <span class="font-semibold text-success">训练中 (Epoch 34/100)</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 数据与特征区 -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <!-- 数据诊断 -->
        <div class="bg-white rounded-xl shadow-card p-6 card-transition hover:shadow-card-hover">
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-xl font-bold text-dark">数据诊断</h2>
            <div class="flex space-x-2">
              <button class="text-dark-2 hover:text-primary transition-colors"><i class="fas fa-ellipsis-v"></i></button>
            </div>
          </div>
          <div class="space-y-6">
            <div>
              <h3 class="text-dark font-semibold mb-4">数据量分布</h3>
              <div ref="dataDistributionRef" class="w-full h-64"></div>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 class="text-dark font-semibold mb-4">缺失值热力图</h3>
                <div ref="missingValuesRef" class="w-full h-48"></div>
              </div>
              <div>
                <h3 class="text-dark font-semibold mb-4">时间覆盖率</h3>
                <div ref="timeCoverageRef" class="w-full h-48"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- 特征概览 -->
        <div class="bg-white rounded-xl shadow-card p-6 card-transition hover:shadow-card-hover">
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-xl font-bold text-dark">特征概览</h2>
            <div class="flex space-x-2">
              <button class="text-dark-2 hover:text-primary transition-colors"><i class="fas fa-expand-alt"></i></button>
              <button class="text-dark-2 hover:text-primary transition-colors"><i class="fas fa-ellipsis-v"></i></button>
            </div>
          </div>
          <div class="mb-6">
            <h3 class="text-dark font-semibold mb-4">特征重要性</h3>
            <div ref="featureImportanceRef" class="w-full h-64"></div>
          </div>
          <div>
            <h3 class="text-dark font-semibold mb-4">特征列表</h3>
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-light-2">
                <thead>
                  <tr>
                    <th class="px-4 py-3 text-left text-xs font-medium text-dark-2 uppercase tracking-wider">特征名称</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-dark-2 uppercase tracking-wider">类型</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-dark-2 uppercase tracking-wider">来源</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-dark-2 uppercase tracking-wider">预处理</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-light-2">
                  <tr class="hover:bg-light-1/50 transition-colors"><td class="px-4 py-3 whitespace-nowrap">昨日排名</td><td class="px-4 py-3 whitespace-nowrap">数值型</td><td class="px-4 py-3 whitespace-nowrap">榜单数据</td><td class="px-4 py-3 whitespace-nowrap">标准化</td></tr>
                  <tr class="hover:bg-light-1/50 transition-colors"><td class="px-4 py-3 whitespace-nowrap">下载量</td><td class="px-4 py-3 whitespace-nowrap">数值型</td><td class="px-4 py-3 whitespace-nowrap">应用商店</td><td class="px-4 py-3 whitespace-nowrap">对数变换+标准化</td></tr>
                  <tr class="hover:bg-light-1/50 transition-colors"><td class="px-4 py-3 whitespace-nowrap">评分</td><td class="px-4 py-3 whitespace-nowrap">数值型</td><td class="px-4 py-3 whitespace-nowrap">应用商店</td><td class="px-4 py-3 whitespace-nowrap">标准化</td></tr>
                  <tr class="hover:bg-light-1/50 transition-colors"><td class="px-4 py-3 whitespace-nowrap">评论数</td><td class="px-4 py-3 whitespace-nowrap">数值型</td><td class="px-4 py-3 whitespace-nowrap">应用商店</td><td class="px-4 py-3 whitespace-nowrap">对数变换+标准化</td></tr>
                  <tr class="hover:bg-light-1/50 transition-colors"><td class="px-4 py-3 whitespace-nowrap">是否周末</td><td class="px-4 py-3 whitespace-nowrap">类别型</td><td class="px-4 py-3 whitespace-nowrap">时间特征</td><td class="px-4 py-3 whitespace-nowrap">独热编码</td></tr>
                </tbody>
              </table>
            </div>
            <div class="mt-3 text-center">
              <button class="text-primary text-sm hover:underline">查看全部 24 个特征 <i class="fas fa-chevron-down ml-1"></i></button>
            </div>
          </div>
        </div>
      </div>

      <!-- 训练过程区 -->
      <div class="bg-white rounded-xl shadow-card p-6 mb-6 card-transition hover:shadow-card-hover">
        <!-- 头部：标题 + 状态/操作 -->
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-xl font-bold text-dark">训练过程</h2>
          <div class="flex items-center space-x-4">
            <div class="flex items-center">
              <span class="text-dark-2 mr-2">当前状态:</span>
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-success/10 text-success">
                <span class="animate-pulse mr-1.5 h-2 w-2 rounded-full bg-success"></span>训练中 (Epoch 34/100)
              </span>
            </div>
            <div class="flex space-x-2">
              <button class="bg-danger/10 hover:bg-danger/20 text-danger px-3 py-1.5 rounded-lg text-sm flex items-center transition-all">
                <i class="fas fa-pause mr-1.5"></i><span> 暂停</span>
              </button>
              <button class="text-dark-2 hover:text-primary transition-colors">
                <i class="fas fa-ellipsis-v"></i>
              </button>
            </div>
          </div>
        </div>

        <!-- 训练与验证指标：整块一行 -->
        <div class="mb-6">
          <h3 class="text-dark font-semibold mb-4">训练与验证指标</h3>
          <div ref="trainingMetricsRef" class="w-full h-72"></div>
        </div>

        <!-- 下排三列：学习率 / 早停 / 资源监控 -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <div>
            <h3 class="text-dark font-semibold mb-4">学习率变化</h3>
            <div ref="learningRateRef" class="w-full h-48"></div>
          </div>

          <div>
            <h3 class="text-dark font-semibold mb-4">早停策略</h3>
            <div class="bg-light-1 rounded-lg p-4 h-48 flex flex-col justify-center items-center">
              <div class="w-16 h-16 rounded-full bg-warning/10 flex items-center justify-center mb-3">
                <i class="fas fa-clock text-warning text-2xl"></i>
              </div>
              <p class="text-dark font-medium mb-1">早停未触发</p>
              <p class="text-dark-2 text-sm text-center">
                当前验证集损失仍在下降<br/>耐心值: 15/20
              </p>
            </div>
          </div>

          <div>
            <h3 class="text-dark font-semibold mb-4">训练资源监控</h3>
            <div ref="resourceUsageRef" class="w-full h-48"></div>
          </div>
        </div>

        <!-- 训练日志：整块一行 -->
        <div>
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-dark font-semibold">训练日志</h3>
            <button class="text-primary text-sm hover:underline">查看完整日志</button>
          </div>
          <div class="bg-dark/5 rounded-lg p-4 h-40 overflow-y-auto scrollbar-hide text-sm font-mono">
            <div class="space-y-2 text-dark-2" ref="logListRef">
              <div class="flex items-start">
                <span class="text-primary mr-2">[20:45:12]</span>
                <span>Epoch 34/100 - Train Loss: 0.0842 - Val Loss: 0.0915</span>
              </div>
              <div class="flex items-start">
                <span class="text-primary mr-2">[20:44:58]</span>
                <span>Train MAE: 0.0621 - Val MAE: 0.0683</span>
              </div>
              <div class="flex items-start">
                <span class="text-primary mr-2">[20:44:58]</span>
                <span>Train RMSE: 0.0935 - Val RMSE: 0.1021</span>
              </div>
              <div class="flex items-start">
                <span class="text-primary mr-2">[20:44:32]</span>
                <span>Learning rate adjusted to: 0.00052</span>
              </div>
              <div class="flex items-start">
                <span class="text-primary mr-2">[20:43:15]</span>
                <span>Epoch 33/100 - Train Loss: 0.0867 - Val Loss: 0.0932</span>
              </div>
              <div class="flex items-start">
                <span class="text-primary mr-2">[20:42:59]</span>
                <span>Train MAE: 0.0638 - Val MAE: 0.0697</span>
              </div>
              <div class="flex items-start">
                <span class="text-primary mr-2">[20:42:59]</span>
                <span>Train RMSE: 0.0958 - Val RMSE: 0.1038</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      <!-- 训练过程区 结束 -->

      <!-- 训练结果与评估区 -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <!-- 核心指标卡片 -->
        <div class="bg-white rounded-xl shadow-card p-6 card-transition hover:shadow-card-hover">
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-xl font-bold text-dark">核心指标</h2>
            <div class="flex space-x-2"><button class="text-dark-2 hover:text-primary transition-colors"><i class="fas fa-ellipsis-v"></i></button></div>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
            <div class="bg-light-1 rounded-lg p-5 text-center"><div class="text-danger text-3xl font-bold mb-1">0.0683</div><div class="text-dark font-medium mb-2">平均绝对误差 (MAE)</div><div class="flex items-center justify-center text-success text-sm"><i class="fas fa-arrow-down mr-1"></i>较上一轮降低 2.1%</div></div>
            <div class="bg-light-1 rounded-lg p-5 text-center"><div class="text-danger text-3xl font-bold mb-1">0.1021</div><div class="text-dark font-medium mb-2">均方根误差 (RMSE)</div><div class="flex items-center justify-center text-success text-sm"><i class="fas fa-arrow-down mr-1"></i>较上一轮降低 1.6%</div></div>
            <div class="bg-light-1 rounded-lg p-5 text-center"><div class="text-success text-3xl font-bold mb-1">0.892</div><div class="text-dark font-medium mb-2">Spearman相关系数</div><div class="flex items-center justify-center text-success text-sm"><i class="fas fa-arrow-up mr-1"></i>较上一轮提升 0.8%</div></div>
            <div class="bg-light-1 rounded-lg p-5 text-center"><div class="text-success text-3xl font-bold mb-1">0.764</div><div class="text-dark font-medium mb-2">NDCG@10</div><div class="flex items-center justify-center text-success text-sm"><i class="fas fa-arrow-up mr-1"></i>较上一轮提升 1.2%</div></div>
          </div>
          <div>
            <h3 class="text-dark font-semibold mb-4">Top-K命中率</h3>
            <div ref="topkHitRateRef" class="w-full h-56"></div>
          </div>
        </div>

        <!-- 模型评估 -->
        <div class="bg-white rounded-xl shadow-card p-6 card-transition hover:shadow-card-hover">
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-xl font-bold text-dark">模型评估</h2>
            <div class="flex space-x-2"><button class="text-dark-2 hover:text-primary transition-colors"><i class="fas fa-ellipsis-v"></i></button></div>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 class="text-dark font-semibold mb-4">误差分布</h3>
              <div ref="errorDistributionRef" class="w-full h-48"></div>
            </div>
            <div>
              <h3 class="text-dark font-semibold mb-4">分组表现</h3>
              <div ref="groupPerformanceRef" class="w-full h-48"></div>
            </div>
          </div>
          <div class="mt-6">
            <h3 class="text-dark font-semibold mb-4">预测vs实际值对比</h3>
            <div ref="predictionVsActualRef" class="w-full h-48"></div>
          </div>
        </div>
      </div>

      <!-- 模型解释区 -->
      <div class="bg-white rounded-xl shadow-card p-6 mb-6 card-transition hover:shadow-card-hover">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-xl font-bold text-dark">模型解释</h2>
          <div class="flex space-x-2"><button class="text-dark-2 hover:text-primary transition-colors"><i class="fas fa-ellipsis-v"></i></button></div>
        </div>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <h3 class="text-dark font-semibold mb-4">SHAP Summary图</h3>
            <div ref="shapSummaryRef" class="w-full h-72"></div>
          </div>
          <div>
            <h3 class="text-dark font-semibold mb-4">样本解释蜂群图</h3>
            <div class="mb-4 flex items-center space-x-3">
              <select class="bg-light-1 border border-light-2 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary">
                <option>样本 #145 (高预测值)</option>
                <option>样本 #289 (中预测值)</option>
                <option>样本 #321 (低预测值)</option>
              </select>
              <button class="bg-primary/10 text-primary px-3 py-2 rounded-lg text-sm hover:bg-primary/20 transition-colors">生成解释报告</button>
            </div>
            <div ref="shapBeeswarmRef" class="w-full h-64"></div>
          </div>
        </div>
      </div>

      <!-- 模型卡与产出区 -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- 模型卡 -->
        <div class="bg-white rounded-xl shadow-card p-6 card-transition hover:shadow-card-hover">
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-xl font-bold text-dark">模型卡</h2>
            <div class="flex space-x-2">
              <button class="bg-primary/10 text-primary px-3 py-1.5 rounded-lg text-sm flex items-center transition-all">
                <i class="fas fa-download mr-1.5"></i> 下载模型
              </button>
              <button class="text-dark-2 hover:text-primary transition-colors"><i class="fas fa-ellipsis-v"></i></button>
            </div>
          </div>
          <div class="space-y-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div><p class="text-dark-2 text-sm mb-1">模型版本</p><p class="font-semibold">v2.3.1</p></div>
              <div><p class="text-dark-2 text-sm mb-1">特征集版本</p><p class="font-semibold">features_v4.2</p></div>
              <div><p class="text-dark-2 text-sm mb-1">数据时间窗</p><p class="font-semibold">2022-01-01 至 2023-06-30</p></div>
              <div><p class="text-dark-2 text-sm mb-1">训练完成时间</p><p class="font-semibold">预计 2023-07-15 22:45</p></div>
            </div>
            <div>
              <p class="text-dark-2 text-sm mb-1">模型校验码</p>
              <p class="font-mono text-sm bg-light-1 p-2 rounded-lg overflow-x-auto scrollbar-hide">7a4f9d2e8c5b1a3f7e9d4c6b2a5f8e7d1c3b5a8f9e6d4c2b1a7f8e9d6c4b</p>
            </div>
            <div>
              <p class="text-dark-2 text-sm mb-1">超参数</p>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm">
                <div class="bg-light-1 p-2 rounded"><span class="font-medium">学习率: </span>0.001 (带衰减)</div>
                <div class="bg-light-1 p-2 rounded"><span class="font-medium">批大小: </span>64</div>
                <div class="bg-light-1 p-2 rounded"><span class="font-medium">LSTM层数: </span>2</div>
                <div class="bg-light-1 p-2 rounded"><span class="font-medium">隐藏层维度: </span>128</div>
                <div class="bg-light-1 p-2 rounded"><span class="font-medium">Dropout: </span>0.2</div>
                <div class="bg-light-1 p-2 rounded"><span class="font-medium">优化器: </span>Adam</div>
              </div>
            </div>
            <div>
              <p class="text-dark-2 text-sm mb-1">局限性</p>
              <div class="bg-warning/10 border border-warning/20 rounded-lg p-3 text-sm">
                <ul class="list-disc list-inside space-y-1 text-dark">
                  <li>对突发市场变化（如新品发布、重大促销）预测能力有限</li>
                  <li>在数据稀疏区域（如新应用）预测误差较大</li>
                  <li>长周期（&gt;14天）预测准确率显著下降</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- 训练日志与导出 -->
        <div class="bg-white rounded-xl shadow-card p-6 card-transition hover:shadow-card-hover">
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-xl font-bold text-dark">训练日志与导出</h2>
            <div class="flex space-x-2"><button class="text-dark-2 hover:text-primary transition-colors"><i class="fas fa-ellipsis-v"></i></button></div>
          </div>
          <div class="mb-6">
            <h3 class="text-dark font-semibold mb-4">导出选项</h3>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <button class="border border-light-2 hover:border-primary bg-white text-dark px-4 py-3 rounded-lg flex items-center justify-center transition-all">
                <i class="fas fa-file-excel text-success text-xl mr-3"></i>
                <div class="text-left"><div class="font-medium">导出指标数据</div><div class="text-dark-2 text-sm">Excel格式</div></div>
              </button>
              <button class="border border-light-2 hover:border-primary bg-white text-dark px-4 py-3 rounded-lg flex items-center justify-center transition-all">
                <i class="fas fa-file-pdf text-danger text-xl mr-3"></i>
                <div class="text-left"><div class="font-medium">导出完整报告</div><div class="text-dark-2 text-sm">PDF格式</div></div>
              </button>
              <button class="border border-light-2 hover:border-primary bg-white text-dark px-4 py-3 rounded-lg flex items-center justify-center transition-all">
                <i class="fas fa-file-code text-info text-xl mr-3"></i>
                <div class="text-left"><div class="font-medium">导出模型代码</div><div class="text-dark-2 text-sm">Python脚本</div></div>
              </button>
              <button class="border border-light-2 hover:border-primary bg-white text-dark px-4 py-3 rounded-lg flex items-center justify-center transition-all">
                <i class="fas fa-database text-warning text-xl mr-3"></i>
                <div class="text-left"><div class="font-medium">导出可视化数据</div><div class="text-dark-2 text-sm">JSON格式</div></div>
              </button>
            </div>
          </div>
          <div>
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-dark font-semibold">最近训练记录</h3>
              <button class="text-primary text-sm hover:underline">查看全部</button>
            </div>
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-light-2">
                <thead>
                  <tr>
                    <th class="px-4 py-3 text-left text-xs font-medium text-dark-2 uppercase tracking-wider">模型名称</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-dark-2 uppercase tracking-wider">状态</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-dark-2 uppercase tracking-wider">完成时间</th>
                    <th class="px-4 py-3 text-left text-xs font-medium text-dark-2 uppercase tracking-wider">操作</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-light-2">
                  <tr class="hover:bg-light-1/50 transition-colors">
                    <td class="px-4 py-3 whitespace-nowrap">LSTM_v2.3.1</td>
                    <td class="px-4 py-3 whitespace-nowrap"><span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-success/10 text-success">训练中</span></td>
                    <td class="px-4 py-3 whitespace-nowrap text-dark-2">进行中</td>
                    <td class="px-4 py-3 whitespace-nowrap">
                      <button class="text-primary hover:text-primary/80 mr-3">查看</button>
                      <button class="text-dark-2 hover:text-primary">日志</button>
                    </td>
                  </tr>
                  <tr class="hover:bg-light-1/50 transition-colors">
                    <td class="px-4 py-3 whitespace-nowrap">LSTM_v2.3.0</td>
                    <td class="px-4 py-3 whitespace-nowrap"><span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-success/10 text-success">已完成</span></td>
                    <td class="px-4 py-3 whitespace-nowrap text-dark-2">2023-07-10 14:32</td>
                    <td class="px-4 py-3 whitespace-nowrap">
                      <button class="text-primary hover:text-primary/80 mr-3">查看</button>
                      <button class="text-dark-2 hover:text-primary">日志</button>
                    </td>
                  </tr>
                  <tr class="hover:bg-light-1/50 transition-colors">
                    <td class="px-4 py-3 whitespace-nowrap">GRU_v1.1.2</td>
                    <td class="px-4 py-3 whitespace-nowrap"><span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-success/10 text-success">已完成</span></td>
                    <td class="px-4 py-3 whitespace-nowrap text-dark-2">2023-07-05 09:15</td>
                    <td class="px-4 py-3 whitespace-nowrap">
                      <button class="text-primary hover:text-primary/80 mr-3">查看</button>
                      <button class="text-dark-2 hover:text-primary">日志</button>
                    </td>
                  </tr>
                  <tr class="hover:bg-light-1/50 transition-colors">
                    <td class="px-4 py-3 whitespace-nowrap">ARIMA_v3.0.1</td>
                    <td class="px-4 py-3 whitespace-nowrap"><span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-danger/10 text-danger">已失败</span></td>
                    <td class="px-4 py-3 whitespace-nowrap text-dark-2">2023-07-01 16:48</td>
                    <td class="px-4 py-3 whitespace-nowrap">
                      <button class="text-primary hover:text-primary/80 mr-3">查看</button>
                      <button class="text-dark-2 hover:text-primary">日志</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref } from 'vue'
import * as echarts from 'echarts'

// refs for charts
const dataDistributionRef = ref<HTMLDivElement|null>(null)
const missingValuesRef = ref<HTMLDivElement|null>(null)
const timeCoverageRef = ref<HTMLDivElement|null>(null)
const featureImportanceRef = ref<HTMLDivElement|null>(null)
const trainingMetricsRef = ref<HTMLDivElement|null>(null)
const learningRateRef = ref<HTMLDivElement|null>(null)
const resourceUsageRef = ref<HTMLDivElement|null>(null)
const topkHitRateRef = ref<HTMLDivElement|null>(null)
const errorDistributionRef = ref<HTMLDivElement|null>(null)
const groupPerformanceRef = ref<HTMLDivElement|null>(null)
const predictionVsActualRef = ref<HTMLDivElement|null>(null)
const shapSummaryRef = ref<HTMLDivElement|null>(null)
const shapBeeswarmRef = ref<HTMLDivElement|null>(null)
const logListRef = ref<HTMLDivElement|null>(null)

// instances
let charts: echarts.ECharts[] = []

onMounted(() => {
  initDataDistributionChart()
  initMissingValuesChart()
  initTimeCoverageChart()
  initFeatureImportanceChart()
  initTrainingMetricsChart()
  initLearningRateChart()
  initResourceUsageChart()
  initTopKHitRateChart()
  initErrorDistributionChart()
  initGroupPerformanceChart()
  initPredictionVsActualChart()
  initShapSummaryChart()
  initShapBeeswarmChart()

  window.addEventListener('resize', resizeAll)
  if (logListRef.value) logListRef.value.parentElement!.scrollTop = logListRef.value.parentElement!.scrollHeight
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeAll)
  charts.forEach(c => c.dispose())
  charts = []
})

function pushChart(el: HTMLDivElement|null, option: echarts.EChartsOption){
  if(!el) return
  const c = echarts.init(el)
  c.setOption(option)
  charts.push(c)
}

// === charts (与原HTML一致) ===
function initDataDistributionChart(){
  const option: echarts.EChartsOption = {
    color: ['#165DFF'],
    tooltip:{ trigger:'axis', axisPointer:{ type:'shadow' }},
    grid:{ left:'3%', right:'4%', bottom:'3%', containLabel:true },
    xAxis:{ type:'category', data:['游戏','社交','工具','娱乐','教育','新闻','购物','其他'], axisLabel:{ rotate:30, interval:0 }},
    yAxis:{ type:'value', name:'样本数量' },
    series:[{ name:'数据量', type:'bar', barWidth:'60%', data:[1280,950,820,780,650,520,480,320]}]
  }
  pushChart(dataDistributionRef.value, option)
}

function initMissingValuesChart(){
  const option: echarts.EChartsOption = {
    tooltip:{ formatter:'{c}% 缺失' },
    grid:{ left:'3%', right:'4%', bottom:'3%', containLabel:true },
    xAxis:{ type:'category', data:['1月','2月','3月','4月','5月','6月'] },
    yAxis:{ type:'category', data:['下载量','排名','评分','评论数','收入'] },
    visualMap:{ min:0, max:15, calculable:true, orient:'horizontal', left:'center', bottom:0, inRange:{ color:['#F0F7FF','#165DFF'] } },
    series:[{ type:'heatmap', data:[
      [0,0,2.3],[0,1,1.1],[0,2,0.5],[0,3,3.2],[0,4,8.7],
      [1,0,1.8],[1,1,0.7],[1,2,0.3],[1,3,2.5],[1,4,6.2],
      [2,0,3.5],[2,1,1.5],[2,2,0.8],[2,3,4.1],[2,4,9.3],
      [3,0,2.1],[3,1,0.9],[3,2,0.4],[3,3,2.8],[3,4,7.5],
      [4,0,1.5],[4,1,0.6],[4,2,0.2],[4,3,2.1],[4,4,5.8],
      [5,0,2.8],[5,1,1.3],[5,2,0.7],[5,3,3.5],[5,4,8.1]
    ], label:{ show:true, formatter:(p:any)=>`${p.data[2]}%`, fontSize:10 } }]
  }
  pushChart(missingValuesRef.value, option)
}

function initTimeCoverageChart(){
  const option: echarts.EChartsOption = {
    color:['#36CFC9'],
    tooltip:{ trigger:'axis', formatter:'{b}: {c}%' },
    grid:{ left:'3%', right:'4%', bottom:'3%', containLabel:true },
    xAxis:{ type:'category', boundaryGap:false, data:['1月','2月','3月','4月','5月','6月'] },
    yAxis:{ type:'value', max:100, name:'覆盖率' },
    series:[{ name:'数据覆盖率', type:'line', data:[92,88,95,90,96,94], smooth:true, markLine:{ data:[{type:'average', name:'平均值'}] } }]
  }
  pushChart(timeCoverageRef.value, option)
}

function initFeatureImportanceChart(){
  const option: echarts.EChartsOption = {
    color:['#FAAD14'],
    tooltip:{ trigger:'axis', axisPointer:{ type:'shadow' }},
    grid:{ left:'3%', right:'4%', bottom:'3%', containLabel:true },
    xAxis:{ type:'value', name:'重要性分数' },
    yAxis:{ type:'category', data:['昨日排名','下载量','评论数','评分','是否周末','价格变动','广告投放','历史波动率'], inverse:true },
    series:[{ name:'特征重要性', type:'bar', data:[0.82,0.75,0.63,0.58,0.42,0.35,0.28,0.21] }]
  }
  pushChart(featureImportanceRef.value, option)
}

function initTrainingMetricsChart(){
  const epochs = 34
  const trainLoss:number[] = [], valLoss:number[] = [], trainMAE:number[] = [], valMAE:number[] = []
  for(let i=1;i<=epochs;i++){
    trainLoss.push(0.3*Math.exp(-i/15)+0.05+Math.random()*0.02)
    valLoss.push(0.35*Math.exp(-i/18)+0.07+Math.random()*0.03)
    trainMAE.push(0.2*Math.exp(-i/15)+0.04+Math.random()*0.01)
    valMAE.push(0.25*Math.exp(-i/18)+0.05+Math.random()*0.02)
  }
  const option: echarts.EChartsOption = {
    tooltip:{ trigger:'axis' },
    legend:{ data:['训练 Loss','验证 Loss','训练 MAE','验证 MAE'], top:0 },
    grid:{ left:'3%', right:'4%', bottom:'3%', containLabel:true },
    xAxis:{ type:'value', name:'Epoch' },
    yAxis:[
      { type:'value', name:'Loss', min:0, max:0.4, position:'left', axisLine:{ show:true, lineStyle:{ color:'#165DFF' } } },
      { type:'value', name:'MAE',  min:0, max:0.3, position:'right', axisLine:{ show:true, lineStyle:{ color:'#FAAD14' } }, splitLine:{ show:false } }
    ],
    series:[
      { name:'训练 Loss', type:'line', yAxisIndex:0, data:trainLoss, smooth:true, lineStyle:{ color:'#165DFF', width:2 }, symbol:'none' },
      { name:'验证 Loss', type:'line', yAxisIndex:0, data:valLoss,   smooth:true, lineStyle:{ color:'#165DFF', width:2, type:'dashed' }, symbol:'none' },
      { name:'训练 MAE', type:'line', yAxisIndex:1, data:trainMAE, smooth:true, lineStyle:{ color:'#FAAD14', width:2 }, symbol:'none' },
      { name:'验证 MAE', type:'line', yAxisIndex:1, data:valMAE,   smooth:true, lineStyle:{ color:'#FAAD14', width:2, type:'dashed' }, symbol:'none' }
    ]
  }
  pushChart(trainingMetricsRef.value, option)
}

function initLearningRateChart(){
  const epochs=34, lrArr:number[]=[], base=0.002
  let lr=base
  for(let i=1;i<=epochs;i++){ if(i%10===0) lr*=0.5; lrArr.push(lr) }
  const option: echarts.EChartsOption = {
    color:['#FF4D4F'],
    tooltip:{ trigger:'axis', formatter:'Epoch {b}: {c}' },
    grid:{ left:'3%', right:'4%', bottom:'3%', containLabel:true },
    xAxis:{ type:'category', data:Array.from({length:epochs},(_,i)=>i+1), name:'Epoch' },
    yAxis:{ type:'log', name:'学习率', axisLabel:{ formatter:'{value}' } },
    series:[{ name:'学习率', type:'line', data:lrArr, step:'end', lineStyle:{ width:2 }, symbol:'none' }]
  }
  pushChart(learningRateRef.value, option)
}

function initResourceUsageChart(){
  const option: echarts.EChartsOption = {
    tooltip:{ trigger:'axis' },
    legend:{ data:['GPU使用率','CPU使用率'], bottom:0 },
    grid:{ left:'3%', right:'4%', bottom:'15%', containLabel:true },
    xAxis:{ type:'category', boundaryGap:false, data:['0s','10s','20s','30s','40s','50s','60s'], name:'时间' },
    yAxis:{ type:'value', max:100, name:'使用率 (%)' },
    series:[
      { name:'GPU使用率', type:'line', data:[65,78,82,75,88,82,76], lineStyle:{ color:'#722ED1' },
        areaStyle:{ color: new (echarts as any).graphic.LinearGradient(0,0,0,1,[{offset:0,color:'rgba(114,46,209,0.3)'},{offset:1,color:'rgba(114,46,209,0)'}])}, smooth:true, symbol:'none' },
      { name:'CPU使用率', type:'line', data:[35,42,38,45,40,36,32], lineStyle:{ color:'#FAAD14' },
        areaStyle:{ color: new (echarts as any).graphic.LinearGradient(0,0,0,1,[{offset:0,color:'rgba(250,173,20,0.3)'},{offset:1,color:'rgba(250,173,20,0)'}])}, smooth:true, symbol:'none' }
    ]
  }
  pushChart(resourceUsageRef.value, option)
}

function initTopKHitRateChart(){
  const option: echarts.EChartsOption = {
    color:['#52C41A'],
    tooltip:{ trigger:'axis', axisPointer:{ type:'shadow' }, formatter:'Top-{b}: {c}%' },
    grid:{ left:'3%', right:'4%', bottom:'3%', containLabel:true },
    xAxis:{ type:'category', data:['5','10','20','50','100'], name:'K值' },
    yAxis:{ type:'value', max:100, name:'命中率 (%)' },
    series:[{ name:'命中率', type:'bar', data:[42,65,78,89,94], label:{ show:true, position:'top', formatter:'{c}%' } }]
  }
  pushChart(topkHitRateRef.value, option)
}

function initErrorDistributionChart(){
  const option: echarts.EChartsOption = {
    color:['#1890FF'],
    tooltip:{ trigger:'axis', axisPointer:{ type:'shadow' } },
    grid:{ left:'3%', right:'4%', bottom:'3%', containLabel:true },
    xAxis:{ type:'category', data:['[-0.2,-0.15)','[-0.15,-0.1)','[-0.1,-0.05)','[-0.05,0)','[0,0.05)','[0.05,0.1)','[0.1,0.15)','[0.15,0.2]'], axisLabel:{ interval:0, rotate:30 }, name:'误差区间' },
    yAxis:{ type:'value', name:'样本数量' },
    series:[{ name:'误差分布', type:'bar', data:[12,35,88,156,142,76,32,15] }]
  }
  pushChart(errorDistributionRef.value, option)
}

function initGroupPerformanceChart(){
  const option: echarts.EChartsOption = {
    tooltip:{ trigger:'axis', axisPointer:{ type:'shadow' } },
    legend:{ data:['MAE'], bottom:0 },
    grid:{ left:'3%', right:'4%', bottom:'15%', containLabel:true },
    xAxis:{ type:'category', data:['游戏','社交','工具','娱乐','教育','其他'], axisLabel:{ rotate:30, interval:0 } },
    yAxis:{ type:'value', name:'MAE' },
    series:[{ name:'MAE', type:'bar', data:[0.058,0.062,0.075,0.068,0.082,0.093],
      itemStyle:{ color:(p:any)=>['#52C41A','#52C41A','#FAAD14','#FAAD14','#FF4D4F','#FF4D4F'][p.dataIndex] } }]
  }
  pushChart(groupPerformanceRef.value, option)
}

function initPredictionVsActualChart(){
  const actual:number[]=[], predicted:number[]=[]
  for(let i=1;i<=14;i++){ actual.push(50+Math.random()*30); predicted.push(actual[i-1]*(0.9+Math.random()*0.2)+(Math.random()-0.5)*5) }
  const option: echarts.EChartsOption = {
    color:['#165DFF','#FAAD14'],
    tooltip:{ trigger:'axis' },
    legend:{ data:['实际值','预测值'], bottom:0 },
    grid:{ left:'3%', right:'4%', bottom:'15%', containLabel:true },
    xAxis:{ type:'category', boundaryGap:false, data:Array.from({length:14},(_,i)=>`Day ${i+1}`), name:'天数' },
    yAxis:{ type:'value', name:'排名' },
    series:[
      { name:'实际值', type:'line', data:actual, smooth:true, symbol:'circle', symbolSize:6 },
      { name:'预测值', type:'line', data:predicted, smooth:true, symbol:'circle', symbolSize:6, lineStyle:{ type:'dashed' } }
    ]
  }
  pushChart(predictionVsActualRef.value, option)
}

function initShapSummaryChart(){
  const features = ['昨日排名','下载量','评论数','评分','是否周末','价格变动','广告投放','历史波动率']
  const data:any[]=[]
  features.forEach((f, idx)=>{ for(let i=0;i<30;i++){ const v=(Math.random()-0.5)*(0.5+idx*0.05); data.push([f, v, Math.abs(v), idx]) } })
  const option: echarts.EChartsOption = {
    title:{ text:'特征对模型输出的影响', left:'center', textStyle:{ fontSize:14, fontWeight:'normal' } },
    tooltip:{ formatter:(p:any)=>`${p.data[0]}: SHAP值 = ${p.data[1].toFixed(3)}` },
    grid:{ left:'15%', right:'8%', bottom:'10%', containLabel:true },
    xAxis:{ type:'value', name:'SHAP值', axisLine:{ show:true } },
    yAxis:{ type:'category', data:[...features].reverse(), axisLine:{ show:false }, axisTick:{ show:false } },
    series:[{ type:'scatter', symbolSize:6, data, itemStyle:{ color:(p:any)=> p.data[1]>0 ? '#FF4D4F' : '#165DFF', opacity:0.7 } }]
  }
  pushChart(shapSummaryRef.value, option)
}

function initShapBeeswarmChart(){
  const features = ['昨日排名','下载量','评论数','评分','是否周末','价格变动','广告投放','历史波动率']
  const data:any[]=[]
  features.forEach((f, idx)=>{ for(let i=0;i<20;i++){ const v=(Math.random()-0.5)*0.8; const fv=Math.random(); data.push([f, v, fv, idx]) } })
  const option: echarts.EChartsOption = {
    tooltip:{ formatter:(p:any)=>`${p.data[0]}: SHAP值 = ${p.data[1].toFixed(3)}<br>特征值: ${p.data[2].toFixed(2)}` },
    grid:{ left:'15%', right:'8%', bottom:'3%', containLabel:true },
    xAxis:{ type:'value', name:'SHAP值', axisLine:{ show:true } },
    yAxis:{ type:'category', data:features, axisLine:{ show:false }, axisTick:{ show:false } },
    series:[{ type:'scatter', data, symbolSize:6, itemStyle:{ color:(p:any)=> `hsl(${p.data[2]*120},70%,50%)`, opacity:0.7 } }]
  }
  pushChart(shapBeeswarmRef.value, option)
}

function resizeAll(){ charts.forEach(c => c.resize()) }
</script>

<style scoped>
/* ===== 等效于原 HTML 中的 @layer utilities 自定义工具类（避免组件内 @tailwind 指令冲突） ===== */
.content-auto { content-visibility: auto; }
.card-transition { transition: all 0.3s ease; }
.scrollbar-hide::-webkit-scrollbar { display: none; }
.scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
.text-balance { text-wrap: balance; }
.grid-cols-card { grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); }

/* ===== Tailwind 主题扩展里使用到的自定义色彩阴影名（需在全局tailwind.config中配置相同token） ===== */
/* 若你的 tailwind.config.js 已包含这些扩展（primary/success/...、shadow-card 等），这里无需再次定义。
   如果没有全局扩展，这些样式可作为回退，保证视觉一致性。 */
.text-dark { color:#1D2129; }
.text-dark-2 { color:#4E5969; }
.bg-light-1 { background:#F2F3F5; }
.bg-light-2 { background:#E5E6EB; }
.border-light-2 { border-color:#E5E6EB; }
.bg-primary { background:#165DFF; }
.text-primary { color:#165DFF; }
.bg-success { background:#52C41A; }
.text-success { color:#52C41A; }
.text-warning { color:#FAAD14; }
.text-danger { color:#FF4D4F; }
.text-info { color:#1890FF; }
.shadow-card { box-shadow: 0 2px 14px 0 rgba(0,0,0,0.06); }
.shadow-card-hover { box-shadow: 0 4px 20px 0 rgba(0,0,0,0.10); }

/* 按钮 hover 辅助（避免 tailwind 扩展缺失导致的差异） */
.bg-primary:hover { filter: brightness(0.95); }
</style>