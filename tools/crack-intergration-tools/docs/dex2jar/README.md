# dex2jar (v2.4)

> 来源: https://github.com/pxb1988/dex2jar/releases/tag/v2.4
> 下载: `dex-tools-v2.4.zip` | 日期: 2026-08-02
> SHA-256: `ee7c45eb3c1d2474a6145d8d447e651a736a22d9664b6d3d3be5a5a817dda23a`

## 角色

- **dex → 真 .class jar**：配合 `convert-smali-to-jars.py`（问题 7）将 smali 汇编的
  `classesN.dex` 转为 `.class` jar，供 `implementation fileTree(dir:'libs')` 原生引用，
  使输出项目不包含任何 smali 目录。

## 位置

- 源码: `tools/crack-intergration-tools/source-projects/dex2jar/`
- 可执行: `tools/crack-intergration-tools/execable/dex2jar/`（lib/*.jar + d2j-dex2jar.sh）

## 用法

```bash
java -cp "tools/crack-intergration-tools/execable/dex2jar/*" \
     com.googlecode.dex2jar.tools.Dex2jarCmd -f -o <out.jar> <input.dex>
```

参数：`-f` 覆盖，`-o <jar>` 指定输出，`-p` 打印 IR，`-r` 复用寄存器。

## 操作链（smali → jar）

```
apktool smali{,classesN}
  → smali 汇编器（~/.gradle cache）→ classesN.dex
    → dex2jar -o smaliN.jar → .class jar
      → app/libs/ → AGP d8 合并进 dex（已用真实游戏 dex 验证 d8 EXIT 0）
```

## 验证记录

- RealmDefenseHeroLegendsTD：smali.jar 9323 .class + smali_classes2.jar 8030 .class，
  d8 --release --min-api 34 消费成功产出 classes.dex + classes2.dex（仅 stack-map 警告）。
