# Project: Limited Infection

Rolling out features on a live web site with active users
requires care to avoid exposing the entire user base
to bad bugs. Features are rolled out slowly, first to a small
subset of users, then to larger and larger sets of users
as bugs are ironed out and the new features are deemed desirable
and robust.

In this particular instance of the feature roll out problem,
we are asked to consider a classroom setting. Ideally,
the entire class is introduced to a feature simultaneously
to avoid confusion between members of the classroom,
students and teachers both, that might see different feature
sets otherwise.

## Running the Implementations


## Coaching Graph Files

Coaching graphs are provided in JSON format.
Two attributes are provided: `users` which is an array of user names;
and `coaches` which is a dictionary with user names as keys and 
arrays of users they coach for values. A simple example with four
users, one of which is the coach, is shown below.

```json
{
    "users": [ "A", "B", "C", "D" ],
    "coaches": {
        "A": [ "B", "C", "D" ]
    }
}
```

## User Model

The original problem description states:

> We can use the heuristic that each teacher­student pair should
be on the same version of the site. So if A coaches B and we want
to give A a new feature, then B should also get the new feature.
Note that infections are transitive ­ if B coaches C, then C should
get the new feature as well. Also, infections are transferred by
both the "coaches" and "is coached by" relations.

An individual user is modeled as a node in a directed graph,
with outgoing edges representing "coaches" relationships,
and incoming edges representing "is coached by" relationships.
Furthermore, users store sets of web site features
that they currently have, which defines the version of the site
they see.  In a very controlled setting, a more limited number
of feature combinations might be allowed and defined by a simple
identifier. To keep the code simple, features are implemented as
strings.

```python
class User(graph.Node):
    """Model users as graph nodes with some special methods."""

    def __init__(self, id, features=set()):
        """Initialize a user with a set of features."""
        _features = set() | features
        super(User, self).__init__(id, _features)

    def features(self):
        """Return the features this user has."""
        return self.data()

    def add_feature(self, feature):
        """Add a web site feature to this user."""
        self.data().add(feature)

    def discard_feature(self, feature):
        """Discard a feature from this user."""
        self.data().discard(feature)

    def coaches(self):
        """Return the set of users this user coaches"""
        return self.outgoing()

    def is_coached_by(self):
        """Return the set of users this user is coached by"""
        return self.incoming()
```

It is important to note that in general, directed graphs might
consist of several **weakly connected components**. It is possible that
a component consists of a single, lonely student or teacher.
Alternatively, everyone could be weakly connected, by some path of
"coaches" and "is coached by" relationships, to everyone else.

## Total Infection

The original problem statement states:

> Starting from any given user, the entire connected component of
the coaching graph containing that user should become infected.

Since a directed graph is used to model the coaching graph,
and infection is spread by "coaches" and "is coached by" relationships,
the **weakly connected component** containing the initial user
is found. All nodes in the component are infected with the feature.
As a slight extension, if a feature starts with an exclamation point (!),
the infection discards the feature.

```python
def total_infection(coaching_graph, initial_user_id, feature):
    """Totally infect a coaching graph with a feature from the initial user"""
    infected = coaching_graph.connected_component(initial_user_id)
    discard = feature.startswith("!")
    for user in infected:
        if discard:
            user.discard_feature(feature[1:]) # strip the leading !
        else:
            user.add_feature(feature)
```

## Limited Infection

Total infection provides limited control over the proportion
of the coaching graph that will be infected. A second part
of the original problem states:

> We would like to be able to infect close to a given number of
users. Ideally we’d like a coach and all of their students to either
have a feature or not. However, that might not always be possible.

```python
def limited_infection(graph, feature, num_users, tolerance):
    """Infect close to a given number of users in the coaching graph."""
```

Some requirements for limited infection:
* If the number of users to infect is > 0, then at least some users
  must be infected.

Some options for limited infection:

* Find all connected components. Search for the collection of
  components that gets closest to the desired number.
* Find all components. If the smallest component is larger than the
  number of users, consider breaking up classes.

## Optional: Exact Limited Infection

One of the optional assignments is to

> write a version of `limited_infection` that infects *exactly* the number
of users specified and fails if that's not possible (this can be (really)
slow)

This assignment is essentially a form of the 
(subset sum problem)[http://en.wikipedia.org/wiki/Subset_sum_problem],
where the multiset of integers consists
of the sizes of the connected components
and -1 times the number of users specified. For example,
if the component sizes are 1, 2, and 3 and the number of desired users
to infect is 4, the subset sum problem would be to find a
non-empty subset of {1, 2, 3, -4} that totals to 0.
This is known to be NP-complete,
meaning no polynomial time algorithm
for all inputs is known to exist.

It is possible to solve though, 
with one naive approach being
to enumerate all possible subsets
of the connected components and stopping
when the sum of their sizes equals
the desired number of infected users.
This naive approach is implemented using recursion
in the code below.

```python
def subset_sum(sizes, target, i, n, subtotal):
    """Solve the subset sum problem recursively."""
    if subtotal == target:
        return [i]

    j = i + 1
    while j < n:
        ret = subset_sum(sizes, target, j, n, subtotal + sizes[j])
        if ret != False:
            if i > -1:
                ret.append(i)
            return ret
        j = j + 1

    return False

def exact_limited_infection(coaching_graph, num_users, feature):
    """Infect a specified number of users exactly in a coaching graph."""
    components = coaching_graph.all_connected_components()
    sizes = [len(x) for x in components]
    solution = subset_sum(sizes, num_users, -1, len(sizes), 0)
    if solution != False:
        for i in solution:
            for user in components[i]:
                user.add_feature(feature)
        return True
    else:
        return False
```

## Possible Improvements

* The recursive subset sum implementation could be modified to use
  tail recursion, where in some languages this could be optimized
  for performance and more efficient stack usage.
