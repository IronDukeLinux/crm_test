var pop_back_id = "";
function pop(url, id) {
    pop_back_id = id;
    // ?pop=1 用于标识这个post提交来自pop而不是一个正常的页面提交，不是返回到查询页面，而是关闭pop
    window.open(url+'?pop=1', url+'?pop=1', "width=800,height=500,top=100,left=100")
}
function pop_back_func(text, pk) {
    var $option = $("<option>");
    $option.text(text);
    $option.val(pk);
    $option.attr("selected", "selected");
    // 在父页面绘制pop页面添加的数据并聚焦
    $("#"+pop_back_id).append($option)
}