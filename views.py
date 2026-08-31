from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from django.http import HttpResponse
import csv
import json
from .models import (
    Expense, Income, Budget, RecurringBill, SavingsGoal, 
    FamilyMember, WeeklyMealPlanner, Category, DebtTracker, ShoppingWishlist
)

@login_required
def dashboard_view(request):
    user_name = "Arfa"

    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    family_filter = request.GET.get('family_member', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    expenses = Expense.objects.filter(user=request.user)
    incomes = Income.objects.filter(user=request.user)

    if search_query:
        expenses = expenses.filter(Q(title__icontains=search_query) | Q(category__icontains=search_query))
    if category_filter:
        expenses = expenses.filter(category=category_filter)
    if family_filter:
        expenses = expenses.filter(family_member_id=family_filter)
    if start_date and end_date:
        expenses = expenses.filter(date__range=[start_date, end_date])
        incomes = incomes.filter(date__range=[start_date, end_date])

    expenses = expenses.order_by('-date')
    incomes = incomes.order_by('-date')

    total_income = incomes.aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    remaining_balance = total_income - total_expense

    avg_daily_expense = float(total_expense) / 30.0 if total_expense else 0.0
    predicted_monthly_expense = round(avg_daily_expense * 30, 2)
    
    smart_tips = []
    if total_expense > total_income and total_income > 0:
        smart_tips.append("⚠️ Over-spending Warning: Aapka kharcha aamdani se zyada hai!")
    elif remaining_balance > 0:
        smart_tips.append("💡 Smart Savings Tip: Aapki remaining balance acchi hai, isay savings goal mein add karein.")
    else:
        smart_tips.append("📌 Expense Insight: Apne daily food aur grocery budget ko optimize karein.")

    goal = SavingsGoal.objects.filter(user=request.user).first()
    savings_goal = goal.target_amount if goal else 0
    savings_progress = min(100, int((remaining_balance / savings_goal * 100))) if savings_goal > 0 else 0

    user_cats = Category.objects.filter(user=request.user).values_list('name', flat=True)
    default_cats = ['Food', 'Groceries', 'Rent', 'Utilities', 'Bill', 'Shopping', 'Other']
    categories = list(set(default_cats + list(user_cats)))

    budget_progress_list = []
    for cat in categories:
        b_obj = Budget.objects.filter(user=request.user, category=cat).first()
        cat_spent = expenses.filter(category=cat).aggregate(Sum('amount'))['amount__sum'] or 0
        limit = b_obj.budget_limit if b_obj else 0
        pct = min(100, int((cat_spent / limit * 100))) if limit > 0 else 0
        budget_progress_list.append({
            'category': cat,
            'spent': cat_spent,
            'limit': limit,
            'percentage': pct
        })

    family_members = FamilyMember.objects.filter(user=request.user)
    meals = WeeklyMealPlanner.objects.filter(user=request.user)
    total_meal_cost = meals.aggregate(Sum('estimated_cost'))['estimated_cost__sum'] or 0

    debts = DebtTracker.objects.filter(user=request.user)
    
    # Total calculation for Debts
    total_give = debts.filter(debt_type='GIVE').aggregate(Sum('amount'))['amount__sum'] or 0
    total_take = debts.filter(debt_type='TAKE').aggregate(Sum('amount'))['amount__sum'] or 0
    net_debt_total = total_give - total_take

    wishlist = ShoppingWishlist.objects.filter(user=request.user)

    chart_labels = categories
    chart_data = [
        float(expenses.filter(category=cat).aggregate(Sum('amount'))['amount__sum'] or 0)
        for cat in categories
    ]

    context = {
        'user_name': user_name,
        'expenses': expenses,
        'incomes': incomes,
        'total_income': total_income,
        'total_expense': total_expense,
        'remaining_balance': remaining_balance,
        'predicted_monthly_expense': predicted_monthly_expense,
        'smart_tips': smart_tips,
        'savings_goal': savings_goal,
        'savings_progress': savings_progress,
        'budget_progress_list': budget_progress_list,
        'family_members': family_members,
        'meals': meals,
        'total_meal_cost': total_meal_cost,
        'categories': categories,
        'debts': debts,
        'total_give': total_give,
        'total_take': total_take,
        'net_debt_total': net_debt_total,
        'wishlist': wishlist,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'search_query': search_query,
        'category_filter': category_filter,
        'family_filter': family_filter,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'dashboard.html', context)

# Dedicated Expense Page
@login_required
def expense_list_view(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        category = request.POST.get('category')
        amount = request.POST.get('amount')
        date = request.POST.get('date')
        member_id = request.POST.get('family_member')
        f_obj = FamilyMember.objects.filter(id=member_id, user=request.user).first() if member_id else None

        Expense.objects.create(user=request.user, title=title, category=category, amount=amount, date=date, family_member=f_obj)
        return redirect('expense_list')

    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    family_members = FamilyMember.objects.filter(user=request.user)
    user_cats = Category.objects.filter(user=request.user).values_list('name', flat=True)
    default_cats = ['Food', 'Groceries', 'Rent', 'Utilities', 'Bill', 'Shopping', 'Other']
    categories = list(set(default_cats + list(user_cats)))

    return render(request, 'expense_list.html', {
        'expenses': expenses,
        'family_members': family_members,
        'categories': categories
    })

@login_required
def delete_expense(request, pk):
    get_object_or_404(Expense, pk=pk, user=request.user).delete()
    return redirect('expense_list')

@login_required
def edit_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        expense.title = request.POST.get('title')
        expense.category = request.POST.get('category')
        expense.amount = request.POST.get('amount')
        expense.date = request.POST.get('date')
        member_id = request.POST.get('family_member')
        expense.family_member = FamilyMember.objects.filter(id=member_id, user=request.user).first() if member_id else None
        expense.save()
        return redirect('expense_list')
    
    family_members = FamilyMember.objects.filter(user=request.user)
    user_cats = Category.objects.filter(user=request.user).values_list('name', flat=True)
    default_cats = ['Food', 'Groceries', 'Rent', 'Utilities', 'Bill', 'Shopping', 'Other']
    categories = list(set(default_cats + list(user_cats)))
    return render(request, 'edit_income.html', {'expense': expense, 'family_members': family_members, 'categories': categories})

# Dedicated Income Page
@login_required
def income_list_view(request):
    if request.method == 'POST':
        source = request.POST.get('source')
        amount = request.POST.get('amount')
        date = request.POST.get('date')
        Income.objects.create(user=request.user, source=source, amount=amount, date=date)
        return redirect('income_list')

    incomes = Income.objects.filter(user=request.user).order_by('-date')
    return render(request, 'income.html', {'incomes': incomes})

@login_required
def delete_income(request, pk):
    get_object_or_404(Income, pk=pk, user=request.user).delete()
    return redirect('income_list')

# Helper Actions
@login_required
def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Category.objects.get_or_create(user=request.user, name=name)
    return redirect('dashboard')

@login_required
def add_debt(request):
    if request.method == 'POST':
        person = request.POST.get('person_name')
        amount = request.POST.get('amount')
        debt_type = request.POST.get('debt_type')
        due_date = request.POST.get('due_date')
        if person and amount:
            DebtTracker.objects.create(
                user=request.user, 
                person_name=person, 
                amount=amount, 
                debt_type=debt_type, 
                due_date=due_date or None
            )
    return redirect('dashboard')

@login_required
def delete_debt(request, pk):
    get_object_or_404(DebtTracker, pk=pk, user=request.user).delete()
    return redirect('dashboard')

@login_required
def add_wishlist(request):
    if request.method == 'POST':
        item = request.POST.get('item_name')
        est_cost = request.POST.get('estimated_cost')
        if item and est_cost:
            ShoppingWishlist.objects.create(user=request.user, item_name=item, estimated_cost=est_cost)
    return redirect('dashboard')

@login_required
def delete_wishlist(request, pk):
    get_object_or_404(ShoppingWishlist, pk=pk, user=request.user).delete()
    return redirect('dashboard')

@login_required
def add_family_member(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        relation = request.POST.get('relation')
        if name:
            FamilyMember.objects.create(user=request.user, name=name, relation=relation)
    return redirect('dashboard')

@login_required
def add_meal_plan(request):
    if request.method == 'POST':
        day = request.POST.get('day')
        meal_name = request.POST.get('meal_name')
        cost = request.POST.get('estimated_cost')
        if day and meal_name:
            WeeklyMealPlanner.objects.create(user=request.user, day=day, meal_name=meal_name, estimated_cost=cost or 0)
    return redirect('dashboard')

@login_required
def delete_meal_plan(request, pk):
    get_object_or_404(WeeklyMealPlanner, pk=pk, user=request.user).delete()
    return redirect('dashboard')

@login_required
def set_savings_goal(request):
    if request.method == 'POST':
        target = request.POST.get('target_amount')
        SavingsGoal.objects.update_or_create(user=request.user, defaults={'target_amount': target})
    return redirect('dashboard')

@login_required
def backup_data(request):
    expenses = list(Expense.objects.filter(user=request.user).values('title', 'category', 'amount', 'date'))
    incomes = list(Income.objects.filter(user=request.user).values('source', 'amount', 'date'))
    data = {'expenses': expenses, 'incomes': incomes}
    response = HttpResponse(json.dumps(data, default=str), content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="arfa_gharkharcha_backup.json"'
    return response

@login_required
def restore_data(request):
    if request.method == 'POST' and request.FILES.get('backup_file'):
        file = request.FILES['backup_file']
        data = json.load(file)
        for item in data.get('expenses', []):
            Expense.objects.create(user=request.user, title=item['title'], category=item['category'], amount=item['amount'], date=item['date'])
        for item in data.get('incomes', []):
            Income.objects.create(user=request.user, source=item['source'], amount=item['amount'], date=item['date'])
    return redirect('dashboard')

@login_required
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="arfa_expenses.csv"'
    writer = csv.writer(response)
    writer.writerow(['Title', 'Category', 'Person', 'Amount', 'Date'])
    for exp in Expense.objects.filter(user=request.user):
        member = exp.family_member.name if exp.family_member else 'Arfa (Self)'
        writer.writerow([exp.title, exp.category, member, exp.amount, exp.date])
    return response

@login_required
def export_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="arfa_expenses_report.pdf"'
    content = "===========================================\n  ARFA GHAR KHARCHA ULTIMATE REPORT\n===========================================\n\n"
    for exp in Expense.objects.filter(user=request.user):
        content += f"Date: {exp.date} | {exp.title} | Cat: {exp.category} | Rs. {exp.amount}\n"
    response.write(content)
    return response