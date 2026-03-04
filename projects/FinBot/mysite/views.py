from django.http import HttpResponse
from django.shortcuts import render
from django.core.files.uploadedfile import SimpleUploadedFile
import os

from .models import AnalysisResult

# Code or video 7
from .langchain_qa import get_answer


def index(request):
    return render(request, "index.html")


def removepunc(request):
    text = request.GET.get("text", "default")
    return HttpResponse(text)


def capfirst(request):
    return HttpResponse("capitalize first")


def newlineremove(request):
    return HttpResponse("capitalize first")


def spaceremove(request):
    return HttpResponse("space remover <a href='/'>Back</a>")


def charcount(request):
    return HttpResponse("charcount ")


def analyze(request):
    djtext = request.GET.get("text", "default")
    usertype = request.GET.get("user", "default")
    usercat = request.GET.get("category", "default")
    userloc = request.GET.get("location", "default")

    p = get_answer(djtext)

    analysis_result = AnalysisResult(
        text=djtext,
        user_type=usertype,
        user_category=usercat,
        user_location=userloc,
        analyzed_text=p,
    )
    analysis_result.save()

    params = {"purpose": "Answer", "analyzed_text": p}

    return render(request, "analyze.html", params)


def feedback(request):
    feedback = request.GET.get("rating", "default")

    print(feedback)
    if feedback == "good":
        analysis_result = AnalysisResult.objects.latest("id")
        analysis_result.improved_text = 1
        analysis_result.save()
        return render(request, "good.html")
    if feedback == "improve":
        return render(request, "feed_bad.html")
    if feedback == "bad":
        return render(request, "feed_bad.html")


def selfimprove(request):
    # Get the text
    feedback = request.GET.get("rating", "default")

    print(feedback)
    if feedback == "myself":
        return render(request, "improve.html")

    if feedback == "admin":
        analysis_result = AnalysisResult.objects.latest("id")
        analysis_result.improved_text = 0
        analysis_result.save()
        return render(request, "good.html")


"""def end(request):
    if request.method == "GET":
        action = request.GET.get("action", "default")

        if action == "link":
            # url_link = request.GET.get("url_link", "")
            url_links = request.GET.getlist("url_link[]", [])
            url_links = [link for link in url_links if link != ""]

            p = get_answer(None, "url_function", url_links)

            params = {"purpose": "Answer", "analyzed_text": p}
            return render(request, "analyze.html", params)

        if action == "write":

            improvement = request.GET.get("improvement", "default")
            analysis_result = AnalysisResult.objects.latest("id")
            analysis_result.improved_text = improvement
            analysis_result.save()

            return render(request, "good.html")
"""


def end(request):
    # url_link = request.GET.get("url_link", "")
    url_links = request.GET.getlist("url_link[]", [])

    improvement = request.GET.get("improvement", "").strip()

    reference_links = request.GET.getlist("reference_link[]", [])

    if url_links != [""] and improvement == "":
        if reference_links != [""]:
            reference_links = [link for link in reference_links if link != ""]
            urls = AnalysisResult.objects.latest("id")
            urls.reference_urls = reference_links
            urls.save()

        url_links = [link for link in url_links if link != ""]
        print("links", url_links)

        p = get_answer(None, "url_function", url_links)

        params = {"purpose": "Answer", "analyzed_text": p}

        return render(request, "analyze.html", params)

    elif improvement != "" and url_links == [""]:
        if reference_links != [""]:
            reference_links = [link for link in reference_links if link != ""]
            print("reference link", reference_links)
            urls = AnalysisResult.objects.latest("id")
            urls.reference_urls = reference_links
            urls.save()

        print("improvement", improvement)
        # improvement = request.GET.get("improvement", "default")
        analysis_result = AnalysisResult.objects.latest("id")
        analysis_result.improved_text = improvement
        analysis_result.save()

        return render(request, "good.html")

    elif improvement != "" and url_links != [""]:
        if reference_links != [""]:
            reference_links = [link for link in reference_links if link != ""]
            urls = AnalysisResult.objects.latest("id")
            urls.reference_urls = reference_links
            urls.save()

        url_links = [link for link in url_links if link != ""]
        print("url links", url_links)

        p = get_answer(None, "url_function", url_links, improvement)

        params = {"purpose": "Answer", "analyzed_text": p}

        return render(request, "analyze.html", params)

    else:
        error_message = "Please provide either URL links, an improvement, or both."
        return render(request, "improve.html", {"error_message": error_message})
