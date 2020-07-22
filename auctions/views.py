from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import *


def index(request):
    active_listings = Listings.objects.filter(active=True)
    return render(request, "auctions/index.html", {
        "listings": active_listings,
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required(login_url="login")
def create(request):
    if request.method == "POST":
        listing = Listings(active=True, title=request.POST["title"], description=request.POST["description"], image=request.POST["image_url"], 
                    category=request.POST["category"], creator=request.user.username)
        listing.save()

        bid = Bids(amount=request.POST["bid"], bidder=request.user.username, listing=listing)
        bid.save()
        return HttpResponseRedirect(reverse("index"))

    return render(request, "auctions/create.html")


def listing(request, id):
    listing = Listings.objects.get(id=id)
    message = None

    try:
        watchlist = listing.watched.get(user=request.user.username)
    except:
        watchlist = None

    if request.method == "POST":
        if "watchlist" in request.POST:
            if request.POST["watchlist"] == "add":
                add = Watchlist(user=request.user.username, lists=listing)
                add.save()
                watchlist = add

            elif request.POST["watchlist"] == "remove":
                watchlist.delete()
                watchlist = None
        
        if "bid" in request.POST:
            bid = int(request.POST["bid"])
            if bid <= listing.bid_listing.get().amount:
                message = "Your bid needs to be larger than the previous one"
            
            else:
                temp = listing.bid_listing.get()
                temp.bidder = request.user.username
                temp.amount = bid
                temp.save()
            
        if "close" in request.POST:
            listing.active = False
            listing.save()
    
    if listing.active == False:
        if listing.bid_listing.get().bidder == request.user.username:
            message = "Congratulations on winning the auction!"
        
        else:
            message = f"The auction was won by {listing.bid_listing.get().bidder}"

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "watchlist": watchlist,
        "message": message
        })