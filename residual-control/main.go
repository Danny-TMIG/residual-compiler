package main

import (
	"embed"
	"log"

	"github.com/wailsapp/wails/v3/pkg/application"
	"residual-control/internal/services"
)

//go:embed all:frontend/dist
var assets embed.FS

func main() {
	svc, err := services.NewAutomationService()
	if err != nil {
		log.Fatal(err)
	}
	defer svc.Close()

	app := application.New(application.Options{
		Name:        "residual-control",
		Description: "Residual automation control panel",
		Assets: application.AssetOptions{
			Handler: application.AssetFileServerFS(assets),
		},
		Services: []application.Service{
			application.NewService(svc),
		},
		OnShutdown: func() {
			_ = svc.Close()
		},
	})

	window := app.Window.New()
	window.Show()

	if err := app.Run(); err != nil {
		log.Fatal(err)
	}
}
