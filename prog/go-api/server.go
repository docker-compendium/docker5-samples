package main

import (
	"encoding/gob"
	"fmt"
	"log"
	"os"

	"github.com/gin-contrib/sessions"
	"github.com/gin-contrib/sessions/redis"
	"github.com/gin-gonic/gin"
)

var router = gin.Default()

func main() {
	log.Println("starting up server")
	port := os.Getenv("PORT")

	if port == "" {
		port = "8000"
	}
	log.Println("Runing on port", port)
	sessionKey := os.Getenv("GO_SESSION_KEY")
	fmt.Println("session key ", sessionKey)
	if sessionKey == "" {
		log.Fatal("error: set GO_SESSION_KEY to a secret string and try again")
	}
	gob.Register(User{})
	store, err := redis.NewStore(10, "tcp", "redis:6379", "", "", []byte(sessionKey))
	if err != nil {
		panic(err)
	}
	// store.Options(sessions.Options{MaxAge: 60 * 60 * 24}) // expire in a day
	router.Use(sessions.Sessions("mysession", store))
	UserRoutes()
	router.Run(fmt.Sprintf(":%s", port))
}
