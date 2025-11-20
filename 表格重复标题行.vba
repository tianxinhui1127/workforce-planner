' 设置Word文档中所有表格的首行为重复标题行
' 功能：遍历文档中的每个表格，并将表格首行设置为在跨页时重复显示
' 错误处理：单个表格处理失败时会自动跳过，继续处理下一个表格
Sub 设置表格重复标题行()
    ' 声明常量以确保代码在所有环境中正常工作
    Const wdCollapseStart = 0
    Const wdCollapseEnd = 1
    Const wdCell = 12
    Const wdExtend = 1
    ' 声明变量
    Dim doc As Document
    Dim tbl As Table
    Dim i As Integer
    Dim successCount As Integer
    Dim errorCount As Integer
    
    ' 初始化计数器
    successCount = 0
    errorCount = 0
    
    ' 错误处理：防止文档未打开时出错
    On Error Resume Next
    ' 设置为当前活动文档
    Set doc = ActiveDocument
    
    ' 检查文档是否成功设置
    If doc Is Nothing Then
        MsgBox "无法访问活动文档，请确保有打开的Word文档。", vbExclamation, "错误"
        Exit Sub
    End If
    On Error GoTo 0 ' 重置错误处理
    
    ' 显示开始处理的消息
    MsgBox "开始处理文档中的" & doc.Tables.Count & "个表格", vbInformation, "表格处理"
    
    ' 遍历文档中的所有表格
    For i = 1 To doc.Tables.Count
        On Error Resume Next ' 启用错误处理，出错时继续执行
        
        ' 获取当前表格
        Set tbl = doc.Tables(i)
        
        ' 检查表格是否存在且至少有一行
        If Not tbl Is Nothing And tbl.Rows.Count >= 1 Then
            ' 清除之前的错误
            Err.Clear
            
            ' 按用户要求：先将光标定位到表格首行，再执行重复标题行操作
            ' 1. 定位到表格首行的第一个单元格
            tbl.Cell(1, 1).Range.Select
            
            ' 2. 扩展选择到整个首行
            Selection.Rows(1).Select
            
            ' 3. 通过Selection对象设置重复标题行
            Selection.Rows.HeadingFormat = True
            
            ' 4. 使用Word命令直接设置（更可靠的方式）
            Selection.Collapse wdCollapseStart
            Selection.MoveRight Unit:=wdCell, Count:=tbl.Columns.Count - 1, Extend:=wdExtend
            Selection.Collapse wdCollapseEnd
            Selection.MoveLeft Unit:=wdCell, Count:=tbl.Columns.Count, Extend:=wdExtend
            Selection.Rows.HeadingFormat = True
            
            ' 验证设置是否成功
            Dim isHeadingFormatSet As Boolean
            isHeadingFormatSet = False
            
            On Error Resume Next
            ' 重新获取表格并检查设置状态
            isHeadingFormatSet = doc.Tables(i).Rows(1).HeadingFormat
            On Error GoTo 0
            
            ' 检查是否发生错误且设置成功
            If Err.Number = 0 And isHeadingFormatSet Then
                successCount = successCount + 1
                Debug.Print "表格 " & i & " 重复标题行设置成功"
            Else
                errorCount = errorCount + 1
                ' 记录错误但继续执行
                Debug.Print "表格 " & i & " 处理失败: " & Err.Description
                If Not isHeadingFormatSet Then
                    Debug.Print "表格 " & i & " HeadingFormat设置未生效"
                End If
            End If
        Else
            errorCount = errorCount + 1
            Debug.Print "表格 " & i & " 不存在或没有行"
        End If
        
        ' 重置错误处理
        On Error GoTo 0
        ' 释放表格对象
        Set tbl = Nothing
    Next i
    
    ' 显示处理结果和详细使用说明
    MsgBox "表格处理完成！" & vbCrLf & _
           "成功处理: " & successCount & "个表格" & vbCrLf & _
           "处理失败: " & errorCount & "个表格" & vbCrLf & vbCrLf & _
           "使用说明：" & vbCrLf & _
           "1. 重复标题行仅在表格跨页时才会显示" & vbCrLf & _
           "2. 请确保表格足够长，跨越至少两页" & vbCrLf & _
           "3. 可以通过打印预览(Ctrl+P)查看效果" & vbCrLf & _
           "4. 如果表格内容不足，可以插入空行使表格跨页" & vbCrLf & _
           "5. 在Word中也可以手动设置：选中表格首行 → 布局选项卡 → 重复标题行", vbInformation, "处理完成"
    
    ' 清理对象
    Set doc = Nothing
End Sub