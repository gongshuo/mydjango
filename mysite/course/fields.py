from django.db import models
from django.core.exceptions import ObjectDoesNotExist


class OrderField(models.PositiveIntegerField):  # ③
    # 得到对象排序的序号，其值为整数，所以继承models.PositiveIntegerField是合适的。
    def __init__(self, for_fields=None, *args, **kwargs):
        self.for_fields = for_fields
        super(OrderField, self).__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):  # ④
        # pre_save()方法的作用是在保存之前对数值进行预处理
        if getattr(model_instance, self.attname) is None:  # ⑤
            # getattr()是Python的内建函数，它能够返回一个对象属性的值
            # self.attname判断当前对象（实例）中是否有某个属性（字段）
            try:
                qs = self.model.objects.all()  # ⑥
                if self.for_fields:
                    query = {field: getattr(model_instance, field) for field in self.for_fields} # ⑦
                    qs = qs.filter(**query)  # ⑧
                    # 根据语句⑤中的数据对语句④的结果进行筛选。
                last_item = qs.latest(self.attname)  # ⑨
                # 根据self.attname得到经过语句⑥筛选之后的记录中的最后一条。
                value = last_item.order + 1  # ⑩
                # 对当前实例进行序号的编排。
            except ObjectDoesNotExist:
                value = 0
            setattr(model_instance, self.attname, value)  # ⑪
            return value
        else:
            return super(OrderField, self).pre_save(model_instance, add)