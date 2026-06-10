from datetime import datetime
import factory
from electronics_store.models import Contacts, Product, Vendor
from users.models import User


class UserFactory(factory.Factory):
    class Meta:
        model = User

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.LazyAttribute(lambda a: '{}.{}@example.com'.format(a.first_name, a.last_name).lower())
    phone_number = factory.Faker('numerify', text='+79#########')
    city = factory.Faker('city')
    is_active = True
    create_at = factory.LazyFunction(datetime.now)
    updated_at = factory.LazyFunction(datetime.now)
    password = factory.Faker('password')


class UserAdminFactory(factory.Factory):
    class Meta:
        model = User

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_staff = True
    is_superuser = True
    email = factory.LazyAttribute(lambda a: '{}.{}@example.com'.format(a.first_name, a.last_name).lower())
    phone_number = factory.Faker('numerify', text='+79#########')
    city = factory.Faker('city')
    is_active = True
    create_at = factory.LazyFunction(datetime.now)
    updated_at = factory.LazyFunction(datetime.now)
    password = factory.Faker('password')


class ContactsFactory(factory.Factory):
    class Meta:
        model = Contacts

    email = factory.Faker('email')
    country = factory.Faker('country')
    city = factory.Faker('city')
    street = factory.Faker('street_name')
    house = factory.Faker('building_number')


class ProductFactory(factory.Factory):
    class Meta:
        model = Product

    name = factory.Faker('company')
    model = factory.Faker('bothify', text='Product Number: ????-########')
    release_date = factory.LazyFunction(datetime.now)


class VendorFactory(factory.Factory):
    class Meta:
        model = Vendor

    name = factory.Faker('company')
    type_point = factory.Faker('random_element', elements=('Индивидуальный предприниматель', 'Розничная сеть'))
    contacts = factory.SubFactory(ContactsFactory)
    products = factory.SubFactory(ProductFactory)
    arrears = factory.Faker('random_int', min=200.00, max=1000000.00)
    release_date = factory.LazyFunction(datetime.now)
    supplier = None

    @factory.post_generation
    def products(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        self.products.add(*extracted)
