
class DirectedGraph:
    def __init__(self):
        self.graph = {}

    def addVertex(self, v):
        if v not in self.graph:
            self.graph[v] = set()

    def addEdge(self, src, dst):
        if src not in self.graph:
            self.addVertex(src)
        if dst not in self.graph:
            self.addVertex(dst)
        self.graph[src].add(dst)

    def removeEdge(self, src, dst):
        """Remove directed edge src -> dst. Return True if removed, False otherwise."""
        if src in self.graph and dst in self.graph[src]:
            self.graph[src].remove(dst)
            return True
        return False

    def listOutgoingAdjacentVertex(self, v):
        return list(self.graph.get(v, []))

    def listIncomingVertices(self, v):
        result = []
        for vertex, edges in self.graph.items():
            if v in edges:
                result.append(vertex)
        return result

    def listVertices(self):
        return list(self.graph.keys())

    def hasEdge(self, src, dst):
        return src in self.graph and dst in self.graph[src]

# Simple Person entity class
class Person:
    def __init__(self, name, gender, biography, privacy='public'):
        self.name = name
        self.gender = gender
        self.biography = biography
        # privacy: 'public' or 'private'
        self.privacy = privacy.lower() if privacy else 'public'

    # Accessor methods matching assignment style
    def getName(self):
        return self.name

    def getGender(self):
        return self.gender

    def getBiography(self):
        return self.biography

    def getPrivacy(self):
        return self.privacy

    def setPrivacy(self, p):
        self.privacy = (p or 'public').lower()

    def __repr__(self):
        return f"Person({self.name}, privacy={self.privacy})"

# SlowGramApp with advanced features
class SlowGramApp:
    def __init__(self):
        self.mygraph = DirectedGraph()
        self.people = []  # keep list for stable ordering / menu indices
        self.enforce_privacy = False  # when True, private profiles hide details

    # ---- Mandatory & Advanced methods ----
    def add_person(self, person):
        """Add person object to list and graph as a vertex."""
        self.people.append(person)
        self.mygraph.addVertex(person)

    def add_follow(self, follower, followed):
        """Create following edge follower -> followed."""
        self.mygraph.addEdge(follower, followed)

    def unfollow(self, follower, followed):
        """Remove following edge follower -> followed. Return bool."""
        return self.mygraph.removeEdge(follower, followed)

    # ---- Display / Query methods ----
    def display_all_profiles(self):
        print("\n========================================")
        print("View All Profile Names:")
        print("========================================")
        for i, p in enumerate(self.people, start=1):
            print(f"{i}) {p.getName()}")

    def display_profile(self, index):
        person = self.people[index - 1]
        print(f"\nName: {person.getName()}")
        # If privacy enforcement is ON and the profile is private -> only show name
        if self.enforce_privacy and person.getPrivacy() == 'private':
            print(f"{person.getName()} has a private profile. (Other details hidden)")
            return
        # Otherwise show full details
        print(f"Gender: {person.getGender()}")
        print(f"Biography: {person.getBiography()}")
        print(f"Privacy: {person.getPrivacy()}")

    def display_followers(self, index):
        person = self.people[index - 1]
        followers = self.mygraph.listIncomingVertices(person)
        print("\nFollower List:")
        if not followers:
            print("- No followers found.")
        else:
            for f in followers:
                print(f"- {f.getName()}")

    def display_following(self, index):
        person = self.people[index - 1]
        following = self.mygraph.listOutgoingAdjacentVertex(person)
        print("\nFollowing List:")
        if not following:
            print("- Not following anyone.")
        else:
            for f in following:
                print(f"- {f.getName()}")

    # ---- Advanced Interactive operations ----
    def add_profile_on_demand(self):
        print("\nAdd New Profile")
        name = input("Name: ").strip()
        if not name:
            print("Name must be provided. Cancelling.")
            return
        gender = input("Gender (optional): ").strip()
        bio = input("Biography (optional): ").strip()
        privacy = input("Privacy (public/private) [public]: ").strip().lower() or 'public'
        if privacy not in ('public', 'private'):
            privacy = 'public'
        new_person = Person(name, gender, bio, privacy)
        self.add_person(new_person)
        print(f"Profile '{new_person.getName()}' added (privacy={new_person.getPrivacy()}).")

    def follow_on_demand(self):
        if len(self.people) < 2:
            print("Need at least two profiles to create a follow.")
            return
        print("\nSelect follower (the person who will follow someone):")
        self.display_all_profiles()
        try:
            i = int(input(f"Follower (1 - {len(self.people)}): ").strip())
            follower = self.people[i - 1]
        except Exception:
            print("Invalid selection. Cancelling.")
            return

        print("\nSelect to-follow (the person to be followed):")
        self.display_all_profiles()
        try:
            j = int(input(f"Followed (1 - {len(self.people)}): ").strip())
            followed = self.people[j - 1]
        except Exception:
            print("Invalid selection. Cancelling.")
            return

        if follower is followed:
            print("A user cannot follow themselves.")
            return

        if self.mygraph.hasEdge(follower, followed):
            print(f"{follower.getName()} is already following {followed.getName()}.")
            return

        self.add_follow(follower, followed)
        print(f"{follower.getName()} now follows {followed.getName()}.")

    def unfollow_on_demand(self):
        print("\nSelect follower (the person who will unfollow someone):")
        self.display_all_profiles()
        try:
            i = int(input(f"Follower (1 - {len(self.people)}): ").strip())
            follower = self.people[i - 1]
        except Exception:
            print("Invalid selection. Cancelling.")
            return

        following = self.mygraph.listOutgoingAdjacentVertex(follower)
        if not following:
            print(f"{follower.getName()} is not following anyone.")
            return

        print("\nSelect which account to unfollow:")
        for idx, p in enumerate(following, start=1):
            print(f"{idx}) {p.getName()}")
        try:
            choice = int(input(f"Unfollow (1 - {len(following)}): ").strip())
            to_unfollow = following[choice - 1]
        except Exception:
            print("Invalid selection. Cancelling.")
            return

        removed = self.unfollow(follower, to_unfollow)
        if removed:
            print(f"{follower.getName()} unfollowed {to_unfollow.getName()}.")
        else:
            print("Unfollow failed (edge not found).")

    def toggle_privacy_enforcement(self):
        self.enforce_privacy = not self.enforce_privacy
        print("Privacy enforcement is now", "ON (private profiles hide details)" if self.enforce_privacy else "OFF (all profiles show details)")

    # ---- Menu ----
    def menu(self):
        while True:
            print("""
*****************************************************
Welcome to Slow Gram, Your New Social Media App:
*****************************************************
1. View names of all profiles
2. View details for any profiles
3. View followers of any profiles
4. View followed accounts of any profiles
5. Add a new profile (optional)
6. Follow someone (optional)
7. Unfollow someone (optional)
8. Toggle privacy enforcement (optional)
9. Quit
*****************************************************
""")
            choice = input("Enter your choice (1 - 9): ").strip()
            if choice == '1':
                self.display_all_profiles()
            elif choice == '2':
                if not self.people:
                    print("No profiles available.")
                    continue
                self.display_all_profiles()
                try:
                    idx = int(input(f"Select whose profile to view (1 - {len(self.people)}): ").strip())
                    if 1 <= idx <= len(self.people):
                        self.display_profile(idx)
                    else:
                        print("Invalid selection.")
                except Exception:
                    print("Invalid input.")
            elif choice == '3':
                if not self.people:
                    print("No profiles available.")
                    continue
                self.display_all_profiles()
                try:
                    idx = int(input(f"Select whose profile to view followers (1 - {len(self.people)}): ").strip())
                    if 1 <= idx <= len(self.people):
                        self.display_followers(idx)
                    else:
                        print("Invalid selection.")
                except Exception:
                    print("Invalid input.")
            elif choice == '4':
                if not self.people:
                    print("No profiles available.")
                    continue
                self.display_all_profiles()
                try:
                    idx = int(input(f"Select whose profile to view followed accounts (1 - {len(self.people)}): ").strip())
                    if 1 <= idx <= len(self.people):
                        self.display_following(idx)
                    else:
                        print("Invalid selection.")
                except Exception:
                    print("Invalid input.")
            elif choice == '5':
                self.add_profile_on_demand()
            elif choice == '6':
                self.follow_on_demand()
            elif choice == '7':
                self.unfollow_on_demand()
            elif choice == '8':
                self.toggle_privacy_enforcement()
            elif choice == '9':
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Try again.")


# ---- Setup sample data and run ----
def main():
    app = SlowGramApp()

    # Create sample profiles
    karen = Person("Karen", "Female", "Coffee lover and cat mom.", "public")
    susy = Person("Susy", "Female", "Just a normal person.", "public")
    brian = Person("Brian", "Male", "Pet photographer.", "private")
    calvin = Person("Calvin", "Male", "Tech & gadget nerd.", "public")
    elon = Person("Elon", "Male", "Collector of ideas.", "public")

    # Add persons (adds vertices)
    for p in (karen, susy, brian, calvin, elon):
        app.add_person(p)

    # Create initial follow edges
    app.add_follow(karen, susy)
    app.add_follow(karen, brian)
    app.add_follow(karen, elon)
    app.add_follow(elon, karen)
    app.add_follow(elon, calvin)
    app.add_follow(brian, karen)
    app.add_follow(brian, susy)
    app.add_follow(calvin, susy)

    # Start CLI menu
    app.menu()

if __name__ == "__main__":
    main()
