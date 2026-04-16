from django.db.models import Q

from .models import Pair


def user_has_any_pair(user):
    return Pair.objects.filter(Q(one=user) | Q(two=user), active=True).exists()


def get_pair_between_users(user_a, user_b):
    return Pair.objects.filter(
        (Q(one=user_a) & Q(two=user_b)) | (Q(one=user_b) & Q(two=user_a)),
        active=True,
    ).first()


def create_pair_between_users(user_a, user_b):
    if user_a == user_b:
        raise ValueError("Nao e possivel criar par com o mesmo usuario.")

    existing_pair = get_pair_between_users(user_a, user_b)
    if existing_pair:
        return existing_pair, False

    if user_has_any_pair(user_a):
        raise ValueError("O usuario que convidou ja possui um par.")
    if user_has_any_pair(user_b):
        raise ValueError("O usuario convidado ja possui um par.")

    pair = Pair.objects.create(one=user_a, two=user_b)
    return pair, True
