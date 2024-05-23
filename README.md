# xcllmtool

The `xcllmtool` is a tool that automatically translates `xcstrings` files using the OpenAI API (ChatGPT). By specifying the source and target languages, ChatGPT will automatically translate the content.



![スクリーンショット 2024-05-22 18.13.28](https://p.ipic.vip/uhcoxs.png)



## Usage

```shell
python main.py [source_xcstrings] \
--api-key "sk-proj-xxxxxxxxxxxxxxxxxxxxxxxx" \
--source en \
--target ja
```

By default, `Localizable.xcstrings` will be translated to `Localizable.translated.xcstrings`.

If `--override` is specified, the file will be overwritten.

## Options

###### Required

- `--api-key`: Open AI API Key
- `-s` `--source`: Source language locale code (like `en`, `ja`, `zh-Hans`... )
- `-t` `--target`: Target language locale code (like `en`, `ja`, `zh-Hans`... )

###### Optional

- `--override`: Override original file.
- `-m` `--model`: Model name. (default: `gpt-4-turbo`)
- `-b` `--batch`: Batch charactor count limit (default: 1000 chars)
- `-r` `--retry`: Retry Count (default: 3)



