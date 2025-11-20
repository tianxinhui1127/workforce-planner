Sub 调整表格行高为最小值()
    ' 声明变量
    Dim doc As Document
    Dim tbl As Table
    Dim tableCount As Integer
    Dim i As Integer
    Dim successCount As Integer
    Dim failedCount As Integer
    Dim progressPercentage As Integer
    
    ' 设置当前文档
    On Error Resume Next
    Set doc = ActiveDocument
    On Error GoTo 0
    
    ' 检查文档是否存在
    If doc Is Nothing Then
        MsgBox "无法访问活动文档！", vbExclamation
        Exit Sub
    End If
    
    ' 初始化计数器
    successCount = 0
    failedCount = 0
    
    ' 获取文档中表格的数量
    tableCount = doc.Tables.Count
    
    ' 检查是否有表格
    If tableCount = 0 Then
        MsgBox "当前文档中没有找到表格！", vbInformation
        Exit Sub
    End If
    
    ' 遍历所有表格
    For i = 1 To tableCount
        ' 计算进度百分比并显示
        progressPercentage = (i / tableCount) * 100
        Application.StatusBar = "正在处理表格 " & i & " / " & tableCount & " (" & progressPercentage & "%)"
        DoEvents ' 允许屏幕更新
        
        ' 获取当前表格
        Set tbl = doc.Tables(i)
        
        ' 添加错误处理
        On Error Resume Next
        
        ' 设置表格自动适应行为为固定列宽
        tbl.AutoFitBehavior wdAutoFitFixed
        
        ' 将表格中所有行的高度设置为最小值
        Dim row As row
        For Each row In tbl.Rows
            ' 设置行高为最小值
            row.HeightRule = wdRowHeightAtLeast ' 使用最小值
            row.Height = InchesToPoints(0.25) ' 设置最小高度值
        Next row
        
        ' 检查是否有错误发生
        If Err.Number = 0 Then
            successCount = successCount + 1
        Else
            failedCount = failedCount + 1
            ' 记录错误信息到调试窗口
            Debug.Print "处理表格 " & i & " 时出错: " & Err.Description
            ' 清除错误
            Err.Clear
        End If
        
        ' 恢复正常错误处理
        On Error GoTo 0
        
        ' 清除对象引用
        Set tbl = Nothing
    Next i
    
    ' 显示完成状态
    Application.StatusBar = "表格行高调整完成!"
    
    ' 显示处理结果统计信息
    Dim message As String
    message = "表格行高调整完成！" & vbCrLf & vbCrLf
    message = message & "总表格数: " & tableCount & vbCrLf
    message = message & "成功调整: " & successCount & vbCrLf
    
    If failedCount > 0 Then
        message = message & "调整失败: " & failedCount & vbCrLf & vbCrLf
        message = message & "请通过 Ctrl+G 打开立即窗口查看详细错误信息。"
    End If
    
    MsgBox message, vbInformation + vbOKOnly, "处理完成"
    
    ' 重置状态栏为默认状态
    Application.StatusBar = False
    
    ' 清除对象引用
    Set doc = Nothing
End Sub