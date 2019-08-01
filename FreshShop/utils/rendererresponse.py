from rest_framework.renderers import JSONRenderer

class customrenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        """

        :param data: 返回的数据
        :param accepted_media_type:接收的类型
        :param renderer_context: 呈现的内容
        :return:
        """
        if renderer_context:  # if request.method == "POST" 如果请求的数据过来
            if isinstance(data, dict):
                msg = data.pop("msg", "请求成功")
                code = data.pop("code", 0)
            else:
                msg = "请求成功"
                code = 0
            ret = {
                "msg": msg,
                "code": code,
                "data": data
            }
            return super().render(ret, accepted_media_type, renderer_context)
        else:
            return super().render(data, accepted_media_type, renderer_context)



