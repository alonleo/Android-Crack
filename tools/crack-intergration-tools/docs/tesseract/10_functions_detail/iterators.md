# Iterators — `PageIterator` / `LTRResultIterator` / `ResultIterator` / `MutableIterator` / `ChoiceIterator`

> **Lifetime warning** (every header repeats): iterators point to data inside
> `TessBaseAPI`. Calling `Init/SetImage/Recognize/Clear/End/DetectOS`
> invalidates them. See `include/tesseract/pageiterator.h:41-44`.

The class hierarchy is documented in [`03_architecture.md §3.2`](../03_architecture.md).
All file:line references below are grep-verified.

---

## `class TESS_API PageIterator` — `include/tesseract/pageiterator.h:50`

### Constructors

#### `PageIterator(PAGE_RES *page_res, Tesseract *tesseract, int scale, int scaled_yres, int rect_left, int rect_top, int rect_width, int rect_height)`
- **签名**: `PageIterator(PAGE_RES *, Tesseract *, int, int, int, int, int, int)`
- **位置**: decl `include/tesseract/pageiterator.h:66`
- **可见性**: public
- **副作用**: 调用 `Begin()`
- **调用**: `ResultIterator` ctor (`src/api/capi.cpp:415` 间接)
- **简要说明**: 主构造器；从 `TessBaseAPI::GetIterator()` 传入

#### `PageIterator(const PageIterator &src)`
- **签名**: `PageIterator(const PageIterator &)`
- **位置**: decl `include/tesseract/pageiterator.h:77`
- **可见性**: public
- **副作用**: 不调用 `Begin()` — 拷贝继续遍历
- **调用**: 用户代码（允许复制 iterator 来嵌套遍历）
- **简要说明**: 拷贝构造；允许多层嵌套遍历

### `virtual ~PageIterator()`
- **位置**: decl `include/tesseract/pageiterator.h` (after `:77`)

### `virtual void Begin()`
- **位置**: decl `include/tesseract/pageiterator.h:89`
- **可见性**: public virtual
- **调用**: 构造器
- **简要说明**: 移到页面开头

### `virtual void RestartParagraph()`
- **位置**: decl `include/tesseract/pageiterator.h:96`
- **简要说明**: 回到段落开头

### `virtual void RestartRow()`
- **位置**: decl `include/tesseract/pageiterator.h:109`
- **简要说明**: 回到行开头

### `virtual bool Next(PageIteratorLevel level)`
- **签名**: `virtual bool Next(PageIteratorLevel level)`
- **位置**: decl `include/tesseract/pageiterator.h:122`
- **可见性**: public virtual
- **返回值**: false 表示到达页面末尾
- **调用**: 用户代码主循环
- **简要说明**: 移到下一个 level 处；`RIL_SYMBOL` 会跳过非文本块

### `virtual bool IsAtBeginningOf(PageIteratorLevel level) const`
- **位置**: decl `include/tesseract/pageiterator.h:137`
- **简要说明**: 判断当前位置是否在某 level 的开头

### `bool IsAtFinalElement(PageIteratorLevel level, PageIteratorLevel el) const`
- **位置**: decl `include/tesseract/pageiterator.h:155`
- **简要说明**: 是否在某 level 的最后一个 el

### `bool Cmp(const PageIterator &other) const`
- **位置**: decl `include/tesseract/pageiterator.h:164`
- **简要说明**: 比较位置

### `void SetBoundingBoxComponents(...)`
- **位置**: decl `include/tesseract/pageiterator.h:188`
- **简要说明**: 设置 bbox 计算组件

### `void BoundingBox(PageIteratorLevel level, int *left, int *top, int *right, int *bottom) const`
- **位置**: decl `include/tesseract/pageiterator.h:203`
- **调用**: 用户代码
- **简要说明**: 取 bbox

### `void Baseline(...)`
- **位置**: decl `include/tesseract/pageiterator.h:261`
- **简要说明**: 取基线坐标

### `void RowAttributes(...)`
- **位置**: decl `include/tesseract/pageiterator.h:265`
- **简要说明**: 取行属性

### `void Orientation(...)`
- **位置**: decl `include/tesseract/pageiterator.h:276`
- **简要说明**: 取方向

### `void ParagraphInfo(...)`
- **位置**: decl `include/tesseract/pageiterator.h:309`
- **简要说明**: 取段落信息

---

## `class TESS_API LTRResultIterator : public PageIterator` — `include/tesseract/ltrresultiterator.h:45`

> Adds text extraction on top of `PageIterator`. For left-to-right scripts.

### `char *GetUTF8Text(PageIteratorLevel level) const`
- **签名**: `char *GetUTF8Text(PageIteratorLevel level) const`
- **位置**: decl `include/tesseract/ltrresultiterator.h:82`
- **可见性**: public
- **返回值**: c-string（caller `delete[]`）
- **调用**: 用户代码；`TessBaseAPI::GetTSVText` 内部 (`src/api/baseapi.cpp:1456`)
- **简要说明**: 取指定 level 的文本

### `int Confidence(PageIteratorLevel level) const`
- **签名**: `int Confidence(PageIteratorLevel level) const`
- **位置**: decl `include/tesseract/ltrresultiterator.h:92`
- **返回值**: 0-100
- **调用**: 用户代码
- **简要说明**: 取置信度

### `void WordFontAttributes(...)`
- **位置**: decl `include/tesseract/ltrresultiterator.h:104`
- **简要说明**: 取词的字体属性（font name, size, bold, italic, underlined, monospace, serif）

### `const char *WordRecognitionLanguage() const`
- **位置**: decl `include/tesseract/ltrresultiterator.h:111`
- **简要说明**: 取词识别所用语言

### `bool WordIsFromDictionary() const`
- **位置**: decl `include/tesseract/ltrresultiterator.h:117`
- **简要说明**: 是否来自字典

### `bool WordIsNumeric() const`
- **位置**: decl `include/tesseract/ltrresultiterator.h:123`
- **简要说明**: 是否纯数字

### `const char *WordTruthUTF8Text() const`
- **位置**: decl `include/tesseract/ltrresultiterator.h:149`
- **简要说明**: 取 ground-truth 文本（仅训练/验证用）

### `void WordLattice(...)`
- **位置**: decl `include/tesseract/ltrresultiterator.h:157`
- **简要说明**: 取 lattice（候选词图）

### `bool SymbolIsSuperscript() const` / `SymbolIsSubscript() const` / `SymbolIsDropcap() const`
- **位置**: decl `include/tesseract/ltrresultiterator.h:164, 168, 172`
- **简要说明**: 取字符排版属性

---

## Nested `class TESS_API ChoiceIterator` — `include/tesseract/ltrresultiterator.h:180`

> Iterates over alternative recognition choices for the current word.

### `bool Next()`
- **位置**: decl `include/tesseract/ltrresultiterator.h:190`
- **调用**: 用户代码
- **简要说明**: 移到下一个候选

### `const char *GetUTF8Text() const`
- **位置**: decl `include/tesseract/ltrresultiterator.h:198`
- **简要说明**: 取候选文本

### `float Confidence() const`
- **位置**: decl `include/tesseract/ltrresultiterator.h:206`
- **简要说明**: 取候选置信度

---

## `class TESS_API ResultIterator : public LTRResultIterator` — `include/tesseract/resultiterator.h:32`

> Adds recognition-specific helpers. Returned by `TessBaseAPI::GetIterator()`.

Only minor extensions over `LTRResultIterator`; see header.

---

## `class TESS_API MutableIterator : public ResultIterator` — `src/ccmain/mutableiterator.h:51`

> Exposes the internal `PAGE_RES_IT *`. For advanced callers.

### `MutableIterator(PAGE_RES *, Tesseract *, int scale, int scaled_yres, int rect_left, int rect_top, int rect_width, int rect_height)`
- **签名**: constructor
- **位置**: decl `src/ccmain/mutableiterator.h:51-60`
- **可见性**: public
- **副作用**: 委托父类构造
- **调用**: `TessBaseAPI::GetMutableIterator` (`src/api/baseapi.cpp:1301`)
- **简要说明**: 通过 `ResultIterator` (→ LTRResultIterator) 构造

### `~MutableIterator() override`
- **位置**: decl `src/ccmain/mutableiterator.h:62`

### `const PAGE_RES_IT *PageResIt() const`
- **签名**: `const PAGE_RES_IT *PageResIt() const`
- **位置**: decl `src/ccmain/mutableiterator.h:64-66`
- **可见性**: public inline
- **调用**: advanced user code
- **简要说明**: 暴露 `PAGE_RES_IT *` — 唯一能直接看 `ccstruct` 内部数据的接口

---

## Iterator usage pattern

```cpp
TessBaseAPI api;
api.Init(datapath, "eng");
api.SetImage(pix);
api.Recognize(nullptr);

std::unique_ptr<ResultIterator> it(api.GetIterator());
while (it->Next(RIL_WORD)) {
    int l, t, r, b;
    it->BoundingBox(RIL_WORD, &l, &t, &r, &b);
    std::unique_ptr<char[]> text(it->GetUTF8Text(RIL_WORD));
    int conf = it->Confidence(RIL_WORD);
    printf("%s [%d] (conf=%d) @ (%d,%d,%d,%d)\n",
           text.get(), strlen(text.get()), conf, l, t, r, b);
}

api.End();
```