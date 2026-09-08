# 去功能点清单

> 由同名 YAML 自动生成；通过 `manage-feature-checklist.py` 增删改查，禁止分别手改两份清单。

YAML 是脚本唯一数据源。每项在项目 hide-plan.yaml / hide-report.yaml 中记录存在性、核心依赖、处理结果和验收证据，不向共享清单写项目状态。

状态：待检查 / 不存在 / 保留（注明核心依赖）/ 已处理待验收 / 验收通过 / 阻塞。关键词命中只是候选，不是自动删除指令。

核心关卡、HUD、设置、皮肤/角色/进度商店及必要回调须保留。处理非核心入口时同时检查节点、调用链和布局占位；不存在某项不能跳过 07/08 阶段。

Frida 仅用于只读查询与侦察；持久修改必须进入工程和 APK，不能依赖 Frida 会话改变游戏状态。

## 功能入口与界面元素（27 项）

| 编号 | 功能点/检查项 | 关键词 | 适用 type | 启用 | 建议策略 | 检查要点 |
|---|---|---|---|---|---|---|
| F01 | 联系我们 | Contact Us / Contact / Feedback / 客服 | * | 是 | review | 隐藏冗余入口并处理外部跳转 |
| F02 | 鸣谢/关于 | Credits / Acknowledgements / About / CreditsButton / ShowCredits / creditScreen | * | 是 | hook_container | 移除目标菜单项及布局占位 |
| F03 | 分享 | Share / ShareButton / ShareManager / ShareGame / OnShare / 分享 | * | 是 | hook_method | 检查入口和仍可达的分享调用 |
| F04 | 隐私政策入口 | PrivacyPolicy / Privacy / OpenPrivacy / privacy_policy / 隐私政策 | * | 是 | hook_method | 检查首启状态依赖，与隐私文本链接分别核查 |
| F05 | 更多游戏 | MoreGames / MoreGamesManager / IMoreGamesManager / More Games / MoreApps / more_games / MoreGamesButton / 更多游戏 | * | 是 | hook_container | 按钮、父布局与推广跳转一起处理 |
| F06 | 礼品店 | Gift Shop / Gifts / 礼品店 | * | 是 | review | 先确认是否承载核心奖励或道具 |
| F07 | 广告入口 | WatchAds / Watch Ads / RewardAd / ShowAds / showAds / InterstitialAd / RewardedAd / ShowAd / 看广告 / 免费金币 | * | 是 | hook_method | 检查奖励完成回调，不切断核心奖励依赖 |
| F08 | 商店入口 | ShopManager / Shop / Store / ShopButton / ShopPanel / OpenShop / 商店 | * | 是 | hook_container | 核心皮肤、角色、进度商店保留，仅处理冗余入口 |
| F09 | 排行榜 | Leaderboard / LeaderBoard / ShowLeaderboard / HighScore / 排行榜 | * | 是 | hook_container | 检查菜单、图标、3D 对象等多个入口与联网跳转 |
| F10 | 社交登录 | Google Login / Facebook Login / 社交登录 | * | 是 | review | 确认离线身份和存档不依赖该入口 |
| F11 | Facebook 连接 | Facebook Connect / Login with FB / FacebookConnect | * | 是 | review | 单独检查连接按钮、状态展示及替代入口 |
| F12 | VIP 按钮 | VIP / VIPMember / VipButton / VIPButton / UnlockVip / vipPanel / VIP 会员 | * | 是 | hook_container | 处理推广按钮与占位，保留核心权益使用路径 |
| F13 | 支付提示按钮 | PaymentPrompt / Recharge / 支付提示 / 充值提示 / 付费引导 | * | 是 | review | 区分购买引导与核心玩法操作 |
| F14 | 版本文本 | Version / VersionText / v1. / 版本号 | * | 是 | hide_node | 检查文本节点及布局，排除系统版本方法 |
| F15 | 头像图标 | Avatar / ProfileIcon / Profile Icon / 头像 | * | 是 | hide_node | 确认不是角色选择或必要状态显示 |
| F16 | 输入框/输入按钮 | Input / TextField / 输入框 | * | 是 | review | 核心命名、解谜或玩法输入必须保留 |
| F17 | 恢复购买 | Restore / RestorePurchase / Restore Purchase / 恢复购买 | * | 是 | hook_method | 不得破坏核心内容恢复与状态完成 |
| F18 | 账户删除 | DeleteAccount / Delete Account / 删除账户 / 注销 | * | 是 | hook_method | 检查仍保留的账户功能与入口依赖 |
| F19 | 隐私政策文本/链接 | Privacy Policy / PrivacyLink / 隐私政策链接 | * | 是 | review | 独立检查文本与链接，避免只移除按钮 |
| F20 | 账号 ID 文本 | Account ID / UID / 账号 ID | * | 是 | review | 确认不是核心状态或必要识别信息 |
| F21 | 转盘 | LuckyWheel / Lucky Wheel / 转盘 / 幸运转盘 | * | 是 | hook_container | 核心玩法或进度依赖的转盘保留 |
| F22 | Logo 图片 | Logo / 游戏图标 / 启动图 | * | 是 | review | 覆盖加载页、主菜单和独立场景实例 |
| F23 | 游戏名标题 | Title / imgTitle / imgtitle / 主菜单标题 / 加载页标题 | * | 是 | review | 文本、图片及同名对象均须核查 |
| F24 | 引擎官方闪屏 | MADE WITH Unity / Unity Logo / 引擎闪屏 | * | 是 | review | 与游戏 Logo 分开检查，按当前引擎版本处理 |
| F25 | 底部白条/系统栏 | NavigationBar / banner / 底部白条 | * | 是 | review | 区分游戏广告/布局和系统导航区域，不能把系统栏当游戏节点删除 |
| F26 | VR Help 按钮与文本 | VR Help / Help / VRHelp | * | 是 | review | 必要玩法帮助保留，父节点与子文本一起检查 |
| F27 | VR Mode 切换 | VR Mode / VRMode / VR | * | 是 | review | 核心 VR 模式保留，同名 Toggle 按身份区分 |

## 弹窗（8 项）

| 编号 | 功能点/检查项 | 关键词 | 适用 type | 启用 | 建议策略 | 检查要点 |
|---|---|---|---|---|---|---|
| P01 | 隐私政策/同意弹窗 | ConsentDialog / Consent / CMP / TOS-PP | * | 是 | review | 检查触发、展示与状态完成；隐藏 UI 不等于同意采集 |
| P02 | 评分弹窗 | RateUs / btnRateUs / Rate Us / RateGame / rateGame / Review / 评分 | * | 是 | hook_method | 检查关卡结束、商店和自动弹出调用 |
| P03 | 更新提示 | Update Available / UpdateDialog / 更新提示 | * | 是 | review | 检查离线能否继续，是否循环阻断 |
| P04 | 通知权限 | POST_NOTIFICATIONS / NotificationPermission | * | 是 | review | 检查请求与后续状态推进 |
| P05 | 广告弹窗 | ShowInterstitial / DisplayAd / Interstitial / 激励视频 | * | 是 | review | 展示路径与奖励/关闭回调分别验收 |
| P06 | 订阅/付费优惠 | Offer / SpecialOffer / Subscription / 订阅 | * | 是 | review | 检查启动、商店、每日奖励及其他自动展示入口 |
| P07 | 新手引导 | Tutorial / Guide / 新手引导 | * | 是 | review | 必要教学保留，检查完成状态是否推进 |
| P08 | 崩溃上报提示 | CrashDialog / CrashReport / 崩溃上报 | * | 是 | review | 检查 UI 阻断，不能以隐藏提示掩盖实际崩溃 |

## 语言选择（4 项）

| 编号 | 功能点/检查项 | 关键词 | 适用 type | 启用 | 建议策略 | 检查要点 |
|---|---|---|---|---|---|---|
| L01 | 按项目要求确定白名单；未另行指定时默认简体中文与 English。 |  | * | 是 | review | 按项目要求确定白名单；未另行指定时默认简体中文与 English。 |
| L02 | 移除白名单外的语言按钮、Tab、国旗与布局占位。 |  | * | 是 | review | 移除白名单外的语言按钮、Tab、国旗与布局占位。 |
| L03 | 动态生成语言选项修改数组/生成源，不能只隐藏当前节点或模板。 |  | * | 是 | review | 动态生成语言选项修改数组/生成源，不能只隐藏当前节点或模板。 |
| L04 | 默认语言、切换语言、退出重入后均正常；索引从当前资源确认。 |  | * | 是 | review | 默认语言、切换语言、退出重入后均正常；索引从当前资源确认。 |

## 真机验收（9 项）

| 编号 | 功能点/检查项 | 关键词 | 适用 type | 启用 | 建议策略 | 检查要点 |
|---|---|---|---|---|---|---|
| V01 | 所有入口和弹窗均有明确检查状态，保留项说明核心依赖。 |  | * | 是 | review | 所有入口和弹窗均有明确检查状态，保留项说明核心依赖。 |
| V02 | 目标入口不可见、不可点击、不可由其他路径触发；无空白、遮挡或拉伸。 |  | * | 是 | review | 目标入口不可见、不可点击、不可由其他路径触发；无空白、遮挡或拉伸。 |
| V03 | 图标/3D 按钮通过画面及交互验证；OCR 无文字或拦截日志不能独立证明隐藏。 |  | * | 是 | review | 图标/3D 按钮通过画面及交互验证；OCR 无文字或拦截日志不能独立证明隐藏。 |
| V04 | 冷启动、加载页、主菜单均无目标游戏名/Logo；引擎闪屏单独检查。 |  | * | 是 | review | 冷启动、加载页、主菜单均无目标游戏名/Logo；引擎闪屏单独检查。 |
| V05 | 语言 Tab/国旗无残留，切换和重入不复现被移除项。 |  | * | 是 | review | 语言 Tab/国旗无残留，切换和重入不复现被移除项。 |
| V06 | 离线可进入核心玩法；关卡、HUD、存档、必要设置与核心商店正常。 |  | * | 是 | review | 离线可进入核心玩法；关卡、HUD、存档、必要设置与核心商店正常。 |
| V07 | 受影响路径无 FATAL/AndroidRuntime、卡等待、循环弹窗，完成存活采样。 |  | * | 是 | review | 受影响路径无 FATAL/AndroidRuntime、卡等待、循环弹窗，完成存活采样。 |
| V08 | 修改随 APK 持久生效，不依赖 Frida；截图与报告写入项目记录。 |  | * | 是 | review | 修改随 APK 持久生效，不依赖 Frida；截图与报告写入项目记录。 |
| V09 | 09 缺设备或验收条件时记录阻塞并暂停；通过后立即更新状态和固化经验脚本。 |  | * | 是 | review | 09 缺设备或验收条件时记录阻塞并暂停；通过后立即更新状态和固化经验脚本。 |

实现选择见 [引擎说明](engine-notes.md)，步骤与阻塞处理见 [阶段接口](stage-contract.md)。

本清单仅涵盖去功能点与弹窗交互，不引入第三方 SDK 的组件删除、注册表或移除方案。
