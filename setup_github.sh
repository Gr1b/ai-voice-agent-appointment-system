#!/bin/bash

# Setup script for deploying to GitHub
# Run this after creating the repository on GitHub

echo "🚀 Setting up GitHub repository for AI Voice Agent Appointment System"

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Error: Not in a git repository. Please run this from the project root."
    exit 1
fi

# Get GitHub username
read -p "Enter your GitHub username: " username

if [ -z "$username" ]; then
    echo "❌ Error: GitHub username is required"
    exit 1
fi

# Set up remote
echo "📡 Adding GitHub remote..."
git remote add origin "https://github.com/$username/ai-voice-agent-appointment-system.git"

# Check if remote was added successfully
if git remote -v | grep -q origin; then
    echo "✅ Remote added successfully"
else
    echo "❌ Error: Failed to add remote"
    exit 1
fi

# Push to GitHub
echo "📤 Pushing to GitHub..."
git branch -M main
git push -u origin main

if [ $? -eq 0 ]; then
    echo "🎉 Successfully deployed to GitHub!"
    echo "📍 Repository URL: https://github.com/$username/ai-voice-agent-appointment-system"
    echo ""
    echo "Next steps:"
    echo "1. Visit your repository on GitHub"
    echo "2. Import the scripts from scripts/ directory into Windmill"
    echo "3. Configure your Supabase resource in Windmill"
    echo "4. Test the scripts with your data"
else
    echo "❌ Error: Failed to push to GitHub"
    echo "Make sure you've created the repository on GitHub first"
    exit 1
fi