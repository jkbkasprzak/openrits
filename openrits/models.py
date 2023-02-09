from django.db import models


class PropertyDefinition(models.Model):
    SUPPORTED_FIELDS = (
        models.IntegerField,
        models.FloatField,
        models.BooleanField,
        models.TextField,
        models.DateField,
    )

    name = models.CharField(max_length=127)
    property_type = models.CharField(
        max_length=63,
        choices=list((t.__name__, t.__name__) for t in SUPPORTED_FIELDS),
    )

    class Meta:
        abstract = True


class PropertyValue(models.Model):
    TYPE_DICT = {t.__name__: t for t in PropertyDefinition.SUPPORTED_FIELDS}

    value = models.TextField(default="")

    def getPropertyType(self) -> str:
        """
        Subclasses should override this and return
        their respective property type as str.
        """
        raise NotImplementedError()

    def deserialize(self) -> any:
        """
        Deserializes value using type returned by getProperty
        """
        property_type = self.getPropertyType()
        return PropertyValue.TYPE_DICT[property_type]().to_python(self.value)

    def serialize(self, object: any):
        """
        Serializes object and writes it to the value
        """
        self.value = str(object)

    class Meta:
        abstract = True


class ItemCategory(models.Model):
    name = models.CharField(max_length=127)
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True)


class ItemCategoryProperty(PropertyDefinition):
    category = models.ForeignKey(ItemCategory, on_delete=models.CASCADE)


class Item(models.Model):
    name = models.CharField(max_length=127)
    amount = models.PositiveIntegerField(default=0)
    archived = models.BooleanField(default=False)
    category = models.ForeignKey(
        ItemCategory, on_delete=models.SET_NULL, null=True, blank=True
    )


class ItemPropertyValue(PropertyValue):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    property = models.ForeignKey(ItemCategoryProperty, on_delete=models.CASCADE)

    def getPropertyType(self) -> str:
        return self.property.property_type


class Customer(models.Model):
    name = models.CharField(max_length=127)
    surname = models.CharField(max_length=127)
    email = models.EmailField()


class CustomerProperty(PropertyDefinition):
    pass


class CustomerPropertyValue(PropertyValue):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    property = models.ForeignKey(CustomerProperty, on_delete=models.CASCADE)

    def getPropertyType(self) -> str:
        return self.property.property_type


class Rent(models.Model):
    created = models.DateTimeField()
    start = models.DateField()
    end = models.DateField()
    issued = models.DateTimeField(null=True, blank=True)
    returned = models.DateTimeField(null=True, blank=True)


class RentProperty(PropertyDefinition):
    pass


class RentPropertyValue(PropertyValue):
    rent = models.ForeignKey(Rent, on_delete=models.CASCADE)
    property = models.ForeignKey(RentProperty, on_delete=models.CASCADE)

    def getPropertyType(self) -> str:
        return self.property.property_type


class RentItems(models.Model):
    amount = models.PositiveIntegerField()
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True)
    rent = models.ForeignKey(Rent, on_delete=models.CASCADE)