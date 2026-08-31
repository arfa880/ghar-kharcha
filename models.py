from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

class FamilyMember(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    relation = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.relation})" if self.relation else self.name

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    family_member = models.ForeignKey(FamilyMember, on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses')

    def __str__(self):
        return f"{self.title} - {self.amount}"

class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    source = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()

    def __str__(self):
        return f"{self.source} - {self.amount}"

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=100)
    budget_limit = models.DecimalField(max_digits=10, decimal_places=2)

class RecurringBill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    is_paid = models.BooleanField(default=False)

class SavingsGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

class WeeklyMealPlanner(models.Model):
    DAY_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    day = models.CharField(max_length=20, choices=DAY_CHOICES)
    meal_name = models.CharField(max_length=200)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.day} - {self.meal_name}"

class DebtTracker(models.Model):
    TRANSACTION_TYPES = [
        ('GIVE', 'Lene Hain (To Receive)'),
        ('TAKE', 'Dene Hain (To Pay)'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    person_name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    debt_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    due_date = models.DateField(null=True, blank=True)
    is_settled = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.person_name} - {self.debt_type} - {self.amount}"

class ShoppingWishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=200)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2)
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0.00)
    is_purchased = models.BooleanField(default=False)

    def __str__(self):
        return self.item_name