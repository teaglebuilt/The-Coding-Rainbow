Model Architecture planning

Membership
-slugs
-type (free, pro, enterprise)
-price
-stripe plan id "stripe account"

UserMembership
-user     (foreignkey to default user)
-stripe customer id
-membership type     (foreignkey to membership)

Subscription
-user membership    (foreign key to user membership)
-stripe subscription id    (foreignkey to user_membership)
-active

Course
-slug
-title
-description
-allowed memberships     (foreing key to membership)


Lesson
-slug
-title
-course    (foreignkey to course)
-position
-video
-thumbnail

Post
-slug
-title
-description
-author  (Foreign Key on Author)
-image

Author
-User   (ForeignKey to default User)
-Membership  (ForeignKet to UserMembership)
-Name
-Profile Image
