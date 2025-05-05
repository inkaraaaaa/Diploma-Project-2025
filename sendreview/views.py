from django.shortcuts import render, get_object_or_404
from .models import Company, Comment, Internship
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

def company_detail(request, company_id):
    company_obj = get_object_or_404(Company, id=company_id)
    comments = Comment.objects.filter(internship__company=company_obj).select_related("user", "internship")

    return render(request, 'company.html', {
        'company': company_obj,
        'comments': comments,
        'user': request.user
    })
@login_required
def add_comment(request, company_id):
    if request.method == "POST":
        user = request.user
        text = request.POST.get("text")
        rating = int(request.POST.get("rating", 0))

        # Ищем стажировку пользователя в компании
        internship = Internship.objects.filter(user=user, company_id=company_id).first()

        # Если стажировка не найдена, возвращаем ошибку
        if not internship:
            return JsonResponse({"error": "You have not interned at this company."}, status=400)

        # Создаем комментарий
        comment = Comment.objects.create(
            internship=internship,
            user=user,
            text=text,
            rating=rating
        )

        return JsonResponse({"success": True})

    return JsonResponse({"error": "Invalid request"}, status=400)
