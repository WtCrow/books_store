from rest_framework import serializers
from .utils import get_specific_object
from .models import BasketItem


class BasketItemCurrentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BasketItem
        fields = ('id', 'count', 'product', 'link', 'link_to_image', 'name', 'price')

    link = serializers.SerializerMethodField()
    link_to_image = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    def get_link(self, item):
        specific_object = get_specific_object(item.product)
        return specific_object.get_absolute_url()

    def get_link_to_image(self, item):
        return item.product.picture_name.name

    def get_name(self, item):
        return item.product.name

    def get_price(self, item):
        return item.product.price

    def validate(self, attrs):
        attrs = super(BasketItemCurrentUserSerializer, self).validate(attrs)
        product = self.instance.product if self.instance else attrs.get('product')

        if self.instance and self.instance.user != self.context['request'].user:
            raise serializers.ValidationError('Wrong user')
        if 'count' in attrs:
            if attrs['count'] > product.count_in_stock:
                raise serializers.ValidationError('Count in stock less than requested count')
            if self.context['request'].method == 'POST' and attrs['count'] == 0:
                raise serializers.ValidationError("Count can't be zero if method POST")
        if self.context['request'].method == 'POST'\
                and BasketItem.objects.filter(product=product, user=self.context['request'].user).exists():
            raise serializers.ValidationError('This product already in basket, use PATH method for update count')

        return attrs

    def update(self, instance, validated_data):
        instance.count = validated_data.get('count')
        if instance.count == 0:
            instance.delete()
        else:
            instance.save()
        return instance

    def create(self, validated_data):
        return BasketItem.objects.create(user=self.context['request'].user, **validated_data)
