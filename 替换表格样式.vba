Sub 应用表格样式()
    ' 声明变量
    Dim doc As Document
    Dim tbl As Table
    Dim tableCount As Integer
    Dim processedCount As Integer
    Dim progressPercentage As Integer
    
    ' 设置文档对象
    On Error Resume Next
    Set doc = ActiveDocument
    On Error GoTo 0
    
    ' 检查文档是否存在
    If doc Is Nothing Then
        MsgBox "无法访问活动文档，请确保Word文档已打开。", vbExclamation + vbOKOnly, "错误"
        Exit Sub
    End If
    
    ' 初始化计数器
    tableCount = doc.Tables.Count
    processedCount = 0
    Dim successCount As Integer
    Dim failedCount As Integer
    successCount = 0
    failedCount = 0
    
    ' 检查是否有表格
    If tableCount = 0 Then
        MsgBox "文档中没有找到表格。", vbInformation + vbOKOnly, "提示"
        Exit Sub
    End If
    
    ' 遍历文档中的所有表格
    For Each tbl In doc.Tables
        ' 更新状态栏显示进度
        progressPercentage = (processedCount / tableCount) * 100
        Application.StatusBar = "正在处理表格: " & processedCount + 1 & "/" & tableCount & " (" & progressPercentage & "%)"
        
        ' 添加错误处理
        On Error Resume Next
        ' 应用"网格表 4 - 着色 1"样式
        tbl.Style = "网格表 4 - 着色 1"
        
        ' 检查是否有错误发生
        If Err.Number = 0 Then
            successCount = successCount + 1
        Else
            failedCount = failedCount + 1
            ' 记录错误信息到调试窗口
            Debug.Print "处理表格时出错: " & Err.Description
            ' 清除错误
            Err.Clear
        End If
        
        On Error GoTo 0
        processedCount = processedCount + 1
        
        ' 允许屏幕更新，使状态栏变化可见
        DoEvents
    Next tbl
    
    ' 更新状态栏为完成状态
    Application.StatusBar = "表格样式应用完成!"
    
    ' 清理对象
    Set tbl = Nothing
    Set doc = Nothing
    
    ' 重置状态栏为默认状态
    Application.StatusBar = False
    
    ' 显示详细的处理结果
    Dim resultMsg As String
    resultMsg = "表格样式应用完成！" & vbCrLf & vbCrLf
    resultMsg = resultMsg & "总表格数: " & tableCount & vbCrLf
    resultMsg = resultMsg & "成功应用样式: " & successCount & vbCrLf
    resultMsg = resultMsg & "应用失败: " & failedCount & vbCrLf & vbCrLf
    
    If failedCount > 0 Then
        resultMsg = resultMsg & "部分表格应用样式失败，请查看调试窗口获取详细错误信息。" & vbCrLf
        resultMsg = resultMsg & "提示：请确保Word中存在""网格表 4 - 着色 1""样式。"
    Else
        resultMsg = resultMsg & "所有表格均已成功应用样式。"
    End If
    
    MsgBox resultMsg, vbInformation + vbOKOnly, "表格样式应用结果"
End Sub