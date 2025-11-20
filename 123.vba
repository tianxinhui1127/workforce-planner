Sub BatchFormatWordDocuments()
    Dim fldr As FileDialog
    Dim sItem As String
    Dim doc As Document
    
    ' 弹出文件夹选择对话框
    Set fldr = Application.FileDialog(msoFileDialogFolderPicker)
    With fldr
        .Title = "选择包含 Word 文档的文件夹"
        .AllowMultiSelect = False
        If .Show = -1 Then
            sItem = .SelectedItems(1)
        Else
            Exit Sub
        End If
    End With
    
    ' 遍历文件夹中的 Word 文档
    sItem = sItem & "\"
    Dim fileName As String
    fileName = Dir(sItem & "*.docx")
    Do While fileName <> ""
        Set doc = Documents.Open(sItem & fileName)
        
        ' 页面设置
        With doc.PageSetup
            .Orientation = wdOrientPortrait ' 纸张方向为纵向
            .PaperSize = wdPaperA4 ' 纸张大小为 A4
            .TopMargin = CentimetersToPoints(2.54) ' 上页边距 2.54cm
            .BottomMargin = CentimetersToPoints(2.54) ' 下页边距 2.54cm
            .LeftMargin = CentimetersToPoints(3.18) ' 左页边距 3.18cm
            .RightMargin = CentimetersToPoints(3.18) ' 右页边距 3.18cm
        End With
        
        FormatAllDocumentElements
        doc.Save
        doc.Close
        fileName = Dir
    Loop
    
    MsgBox "所有文档格式化完成！", vbInformation, "格式化完成"
End Sub

Sub FormatAllDocumentElements()
    ' 调用各个格式化子过程
    FormatTableAndTextboxParagraphs ' 新增调用，处理表格和文本框格式
    FormatParagraphs ' 新增调用，处理普通段落
    FormatTitleParagraphs ' 新增调用，处理标题段落
    FormatTables ' 新增调用，处理表格单元格边距和随窗口调整
    MsgBox "文档格式化完成！", vbInformation, "格式化完成"
End Sub

Sub FormatTableAndTextboxParagraphs()
    Dim para As Paragraph
    Dim shp As Shape
    Dim subShp As Shape
    Dim rng As Range
            
    ' 处理表格中的段落
    For Each para In ActiveDocument.Paragraphs
        ' 检查段落是否在表格内
        If para.Range.Tables.Count > 0 Then
            FormatParaFontAndParaFormat para.Range
        End If
    Next para
    
    ' 处理文本框中的段落，包括组合图形中的文本框
    For Each shp In ActiveDocument.Shapes
        If shp.Type = msoGroup Then
            For Each subShp In shp.GroupItems
                If subShp.Type = msoTextBox Then
                    For Each para In subShp.TextFrame.TextRange.Paragraphs
                        FormatParaFontAndParaFormat para.Range
                    Next para
                End If
            Next subShp
        ElseIf shp.Type = msoTextBox Then
            For Each para In shp.TextFrame.TextRange.Paragraphs
                FormatParaFontAndParaFormat para.Range
            Next para
        End If
    Next shp
End Sub

' 定义一个名为 FormatParagraphs 的子过程，用于格式化文档中的非表格段落
Sub FormatParagraphs()
    ' 声明一个 Paragraph 类型的变量 para，用于在循环中表示当前处理的段落
    Dim para As Paragraph
    ' 遍历文档中的每一个段落
    For Each para In ActiveDocument.Paragraphs
        ' 检查当前段落是否不在表格内
        If para.Range.Tables.Count = 0 Then
            FormatNonTableParaFontAndParaFormat para.Range
        End If
    Next para
End Sub

' 新增子过程，处理标题段落
Sub FormatTitleParagraphs()
    Dim para As Paragraph
    For Each para In ActiveDocument.Paragraphs
        ' 检查段落是否应用了标题样式
        If para.Style.NameLocal Like "标题*" Then
            ' 先应用正文格式
            FormatNonTableParaFontAndParaFormat para.Range
            ' 再设置字体为 3 号黑体
            With para.Range.Font
                .NameFarEast = "黑体"
                .NameAscii = "黑体"
                .NameOther = "黑体"
                .Name = "黑体"
                .Size = 16 ' 3 号字体对应的磅值是 16
            End With
        End If
    Next para
End Sub
' 新增子过程，处理表格
Sub FormatTables()
    Dim tbl As Table
    For Each tbl In ActiveDocument.Tables
        ' 调整表格单元格边距上下左右均为 0
        With tbl
           .Rows.HeightRule = wdRowHeightAuto
           .AllowAutoFit = True
           ' 根据窗口自动调整表格
           .AutoFitBehavior (wdAutoFitWindow)
            For Each cell In .Range.Cells
                With cell
                   .TopPadding = 0
                   .BottomPadding = 0
                   .LeftPadding = 0
                   .RightPadding = 0
                End With
            Next cell
        End With
    Next tbl
End Sub

' 定义一个名为 FormatParaFontAndParaFormat 的函数，用于设置字体和段落格式
Sub FormatParaFontAndParaFormat(ByVal rng As Range)
    ' 对表格段落的字体格式进行设置
    With rng.Font
        ' 设置中文字体为宋体
        .NameFarEast = "宋体"
        ' 设置英文字体为 宋体
        .NameAscii = "宋体"
        ' 设置其他字符的字体为 宋体
        .NameOther = "宋体"
        ' 设置字体大小为 10.5 磅（五号）
        .Size = 10.5
        ' 取消加粗效果
        .Bold = False
        ' 取消倾斜效果
        .Italic = False
        ' 取消下划线
        .Underline = wdUnderlineNone
        ' 设置下划线颜色为自动默认颜色
        .UnderlineColor = wdColorAutomatic
        ' 取消删除线效果
        .StrikeThrough = False
        ' 取消双删除线效果
        .DoubleStrikeThrough = False
        ' 取消轮廓效果
        .Outline = False
        ' 取消浮雕效果
        .Emboss = False
        ' 取消阴影效果
        .Shadow = False
        ' 取消隐藏效果
        .Hidden = False
        ' 取消小型大写字母效果
        .SmallCaps = False
        ' 取消全部大写字母效果
        .AllCaps = False
        ' 设置字体颜色为黑色
        .Color = wdColorBlack
        ' 取消雕刻效果
        .Engrave = False
        ' 取消上标效果
        .Superscript = False
        ' 取消下标效果
        .Subscript = False
        ' 设置字符间距为 0
        .Spacing = 0
        ' 设置字符缩放比例为 100%
        .Scaling = 100
        ' 设置字符垂直位置为 0
        .Position = 0
        ' 设置字符字距调整为默认值
        .Kerning = 0
        ' 取消字符动画效果
        .Animation = wdAnimationNone
        ' 不禁用字符网格对齐
        .DisableCharacterSpaceGrid = False
        ' 取消强调标记
        .EmphasisMark = wdEmphasisMarkNone
        ' 设置连字规则为默认值
        .Ligatures = wdLigaturesDefault
        ' 设置数字间距为默认值
        .NumberSpacing = wdNumberSpacingDefault
        ' 设置数字格式为默认值
        .NumberForm = wdNumberFormDefault
        ' 设置样式集为默认值
        .StylisticSet = wdStylisticSetDefault
        ' 设置上下文替代为默认值
        .ContextualAlternates = 0
    End With
    ' 对当前段落的段落格式进行设置
    With rng.ParagraphFormat
        ' 设置段落左缩进为 0 厘米（转换为磅值）
        .LeftIndent = CentimetersToPoints(0)
        ' 设置段落右缩进为 0 厘米（转换为磅值）
        .RightIndent = CentimetersToPoints(0)
        ' 设置段前间距为 0 磅
        .SpaceBefore = 0
        ' 取消段前间距自动调整
        .SpaceBeforeAuto = False
        ' 设置段后间距为 0 磅
        .SpaceAfter = 0
        ' 取消段后间距自动调整
        .SpaceAfterAuto = False
         ' 设置行间距规则为固定值
        .LineSpacingRule = wdLineSpaceExactly
        ' 设置行间距为 26 磅
        .LineSpacing = 26
        ' 设置段落对齐方式为两端对齐
        .Alignment = wdAlignParagraphJustify
        ' 取消孤行控制
        .WidowControl = False
        ' 不与下一段保持在同一页
        .KeepWithNext = False
        ' 不保持段落内容在同一页
        .KeepTogether = False
        ' 不在段落前强制分页
        .PageBreakBefore = False
        ' 不取消行号显示
        .NoLineNumber = False
        ' 启用自动断字功能
        .Hyphenation = True
        ' 设置段落大纲级别为正文文本
        .OutlineLevel = wdOutlineLevelBodyText
        ' 设置段落左缩进的字符单位为 0
        .CharacterUnitLeftIndent = 0
        ' 设置段落右缩进的字符单位为 0
        .CharacterUnitRightIndent = 0
        ' 设置首行缩进为 3.5 厘米（转换为磅值）
        .FirstLineIndent = CentimetersToPoints(3.5)        
        ' 设置首行缩进的字符单位为 2
        .CharacterUnitFirstLineIndent = 2
        ' 设置段前间距的行单位为 0
        .LineUnitBefore = 0
        ' 设置段后间距的行单位为 0
        .LineUnitAfter = 0
        ' 取消缩进镜像
        .MirrorIndents = False
        ' 设置文本框紧密环绕方式为无
        .TextboxTightWrap = wdTightNone
        ' 不默认折叠段落
        .CollapsedByDefault = False
        ' 不自动调整右缩进
        .AutoAdjustRightIndent = False
        ' 禁用行高网格
        .DisableLineHeightGrid = True
        ' 启用远东换行控制
        .FarEastLineBreakControl = True
        ' 启用单词换行
        .WordWrap = True
        ' 启用悬挂标点
        .HangingPunctuation = True
        ' 不在行首使用半角标点
        .HalfWidthPunctuationOnTopOfLine = False
        ' 在远东字符和字母之间添加空格
        .AddSpaceBetweenFarEastAndAlpha = True
        ' 在远东字符和数字之间添加空格
        .AddSpaceBetweenFarEastAndDigit = True
        ' 设置基线对齐方式为自动
        .BaseLineAlignment = wdBaselineAlignAuto
    End With
End Sub

Sub FormatNonTableParaFontAndParaFormat(ByVal rng As Range)
    ' 对正文部分段落的字体格式进行设置
    With rng.Font
        ' 设置中文字体为宋体
        .NameFarEast = "宋体"
        ' 设置英文字体为宋体
        .NameAscii = "宋体"
        ' 设置其他字符的字体为 宋体
        .NameOther = "宋体"
        ' 设置整体字体为 宋体
        .Name = "宋体"
        ' 设置字体大小为 14 磅（四号）
        .Size = 14
        ' 取消加粗效果
        .Bold = False
        ' 取消倾斜效果
        .Italic = False
        ' 取消下划线
        .Underline = wdUnderlineNone
        ' 设置下划线颜色为自动默认颜色
        .UnderlineColor = wdColorAutomatic
        ' 取消删除线效果
        .StrikeThrough = False
        ' 取消双删除线效果
        .DoubleStrikeThrough = False
        ' 取消轮廓效果
        .Outline = False
        ' 取消浮雕效果
        .Emboss = False
        ' 取消阴影效果
        .Shadow = False
        ' 取消隐藏效果
        .Hidden = False
        ' 取消小型大写字母效果
        .SmallCaps = False
        ' 取消全部大写字母效果
        .AllCaps = False
        ' 设置字体颜色，这里使用了特定的颜色代码
        .Color = -587137025
        ' 取消雕刻效果
        .Engrave = False
        ' 取消上标效果
        .Superscript = False
        ' 取消下标效果
        .Subscript = False
        ' 设置字符间距为 0
        .Spacing = 0
        ' 设置字符缩放比例为 100%
        .Scaling = 100
        ' 设置字符垂直位置为 0
        .Position = 0
        ' 设置字符字距调整为 1
        .Kerning = 1
        ' 取消字符动画效果
        .Animation = wdAnimationNone
        ' 不禁用字符网格对齐
        .DisableCharacterSpaceGrid = False
        ' 取消强调标记
        .EmphasisMark = wdEmphasisMarkNone
        ' 设置连字规则为标准上下文连字
        .Ligatures = wdLigaturesStandardContextual
        ' 设置数字间距为默认值
        .NumberSpacing = wdNumberSpacingDefault
        ' 设置数字格式为默认值
        .NumberForm = wdNumberFormDefault
        ' 设置样式集为默认值
        .StylisticSet = wdStylisticSetDefault
        ' 设置上下文替代为 0
        .ContextualAlternates = 0
    End With
    ' 对当前段落的段落格式进行设置
    With rng.ParagraphFormat
        ' 设置段落左缩进为 0 厘米（转换为磅值）
        .LeftIndent = CentimetersToPoints(0)
        ' 设置段落右缩进为 0 厘米（转换为磅值）
        .RightIndent = CentimetersToPoints(0)
        ' 设置段前间距为 0 磅
        .SpaceBefore = 0
        ' 取消段前间距自动调整
        .SpaceBeforeAuto = False
        ' 设置段后间距为 0 磅
        .SpaceAfter = 0
        ' 取消段后间距自动调整
        .SpaceAfterAuto = False
        ' 设置行间距规则为固定值
        .LineSpacingRule = wdLineSpaceExactly
        ' 设置行间距为 26 磅
        .LineSpacing = 26
        ' 设置段落对齐方式为两端对齐
        .Alignment = wdAlignParagraphJustify
        ' 取消孤行控制
        .WidowControl = False
        ' 不与下一段保持在同一页
        .KeepWithNext = False
        ' 不保持段落内容在同一页
        .KeepTogether = False
        ' 不在段落前强制分页
        .PageBreakBefore = False
        ' 不取消行号显示
        .NoLineNumber = False
        ' 启用自动断字功能
        .Hyphenation = True
        ' 设置段落大纲级别为正文文本
        .OutlineLevel = wdOutlineLevelBodyText
        ' 设置段落左缩进的字符单位为 0
        .CharacterUnitLeftIndent = 0
        ' 设置段落右缩进的字符单位为 0
        .CharacterUnitRightIndent = 0
        ' 设置首行缩进为 3.5 厘米（转换为磅值）
        .FirstLineIndent = CentimetersToPoints(3.5)
        ' 设置首行缩进的字符单位为 2
        .CharacterUnitFirstLineIndent = 2
        ' 设置段前间距的行单位为 0
        .LineUnitBefore = 0
        ' 设置段后间距的行单位为 0
        .LineUnitAfter = 0
        ' 取消缩进镜像
        .MirrorIndents = False
        ' 设置文本框紧密环绕方式为无
        .TextboxTightWrap = wdTightNone
        ' 不默认折叠段落
        .CollapsedByDefault = False
        ' 不自动调整右缩进
        .AutoAdjustRightIndent = False
        ' 禁用行高网格
        .DisableLineHeightGrid = True
        ' 启用远东换行控制
        .FarEastLineBreakControl = True
        ' 启用单词换行
        .WordWrap = True
        ' 启用悬挂标点
        .HangingPunctuation = True
        ' 不在行首使用半角标点
        .HalfWidthPunctuationOnTopOfLine = False
        ' 在远东字符和字母之间添加空格
        .AddSpaceBetweenFarEastAndAlpha = True
        ' 在远东字符和数字之间添加空格
        .AddSpaceBetweenFarEastAndDigit = True
        ' 设置基线对齐方式为自动
        .BaseLineAlignment = wdBaselineAlignAuto
    End With
End Sub
